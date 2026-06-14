#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RuneForge downloader integration.

Downloads RuneForge .fantome/.zip artifacts into Aurelia's existing custom mod
storage without changing the skin injection path.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse
import re

import requests

from config import APP_USER_AGENT, DEFAULT_SKIN_DOWNLOAD_TIMEOUT_S
from injection.mods.storage import ModStorageService
from utils.core.logging import get_logger
from utils.core.paths import get_skins_dir
from utils.core.utilities import get_champion_id_from_skin_id

log = get_logger()

RUNEFORGE_BASE_URL = "https://runeforge.dev"
CDRAGON_SKINS_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/skins.json"
ALLOWED_ASSET_HOSTS = {"r2-prod.runeforge.dev", "r2-images-prod.runeforge.dev"}
DOWNLOAD_EXTENSIONS = {".fantome", ".zip"}


@dataclass(frozen=True)
class RuneForgeDownloadResult:
    title: str
    source_url: str
    asset_url: str
    saved_path: Path
    target: str
    skin_hint: str | None = None


class RuneForgeDownloadError(RuntimeError):
    """Raised when a RuneForge page cannot be downloaded or parsed."""


def normalize_runeforge_url(value: str) -> str:
    """Accept a full RuneForge URL or a bare mod UUID and return a mod URL."""
    raw = (value or "").strip()
    if not raw:
        raise RuneForgeDownloadError("Paste a RuneForge mod URL or mod id.")

    if re.fullmatch(r"[0-9a-fA-F-]{32,36}", raw):
        return f"{RUNEFORGE_BASE_URL}/mods/{raw}"

    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        raise RuneForgeDownloadError("Only http/https RuneForge URLs are supported.")
    if parsed.netloc.lower() not in {"runeforge.dev", "www.runeforge.dev"}:
        raise RuneForgeDownloadError("Only runeforge.dev mod URLs are supported.")
    if not parsed.path.startswith("/mods/"):
        raise RuneForgeDownloadError("The URL must point to a RuneForge mod page.")
    return raw


def _page_text(html: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _extract_title(html: str) -> str:
    for pattern in (
        r'<meta\s+property="og:title"\s+content="([^"]+)"',
        r"<title>(.*?)</title>",
    ):
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            title = unescape(match.group(1)).strip()
            return re.sub(r"\s*\|\s*Runeforge\s*$", "", title, flags=re.IGNORECASE) or "RuneForge Mod"
    return "RuneForge Mod"


def _extract_skin_hint(html: str) -> str | None:
    text = _page_text(html)
    match = re.search(r"\bSkin:\s*(.+?)(?:\s+Contact:|\s+Details\b|\s+Category\b|$)", text, flags=re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip(" -")
    return value or None


def _extract_asset_url(html: str) -> str:
    patterns = (
        r"https://r2-prod\.runeforge\.dev/[^\"<>\\]+?\.(?:fantome|zip)(?:\?filename=[^\"<>\\]+)?",
        r"assetUrl[^h]+(https://[^\"\\]+?\.(?:fantome|zip)(?:\?filename=[^\"\\]+)?)",
    )
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if match:
            return unescape(match.group(1) if match.lastindex else match.group(0)).rstrip("\\")
    raise RuneForgeDownloadError("No downloadable .fantome/.zip release was found on this RuneForge page.")


def _validate_asset_url(asset_url: str) -> None:
    parsed = urlparse(asset_url)
    if parsed.scheme != "https" or parsed.netloc.lower() not in ALLOWED_ASSET_HOSTS:
        raise RuneForgeDownloadError("RuneForge returned an unexpected download host.")

    filename = _filename_from_asset_url(asset_url)
    if Path(filename).suffix.lower() not in DOWNLOAD_EXTENSIONS:
        raise RuneForgeDownloadError("RuneForge download must be a .fantome or .zip file.")


def _filename_from_asset_url(asset_url: str) -> str:
    parsed = urlparse(asset_url)
    filename_values = parse_qs(parsed.query).get("filename")
    if filename_values:
        filename = unquote(filename_values[0])
    else:
        filename = unquote(Path(parsed.path).name)
    filename = Path(filename).name.strip()
    if not filename:
        filename = "runeforge-mod.fantome"
    suffix = Path(filename).suffix.lower()
    if suffix not in DOWNLOAD_EXTENSIONS:
        filename = f"{filename}.fantome"
    return filename


def _safe_title(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', " ", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:90] or "RuneForge Mod"


def _target_directory(storage: ModStorageService, skin_id: int | None) -> tuple[Path, str]:
    if skin_id is not None:
        champion_id = get_champion_id_from_skin_id(skin_id)
        if champion_id is not None:
            return get_skins_dir() / str(champion_id) / str(skin_id), f"skins/{champion_id}/{skin_id}"
        log.warning("[RuneForge] Could not infer champion id for skin id %s; using mod storage fallback", skin_id)
        return storage.get_skin_dir(skin_id), f"mods/skins/{skin_id}"
    return storage.mods_root / storage.CATEGORY_OTHERS, storage.CATEGORY_OTHERS


def _normalize_skin_name(value: str) -> str:
    normalized = value.casefold()
    normalized = re.sub(r"\b(base|original|default)\b", "", normalized)
    normalized = re.sub(r"\bskin\b", "", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _infer_skin_id_from_hint(session: requests.Session, skin_hint: str | None) -> int | None:
    """Best-effort skin id inference from RuneForge's visible skin hint."""
    if not skin_hint:
        return None

    wanted = _normalize_skin_name(skin_hint)
    if not wanted:
        return None

    try:
        response = session.get(CDRAGON_SKINS_URL, timeout=DEFAULT_SKIN_DOWNLOAD_TIMEOUT_S)
        response.raise_for_status()
        skins = response.json()
    except Exception as exc:  # noqa: BLE001
        log.warning("[RuneForge] Could not fetch CommunityDragon skins for id inference: %s", exc)
        return None

    exact_match: int | None = None
    base_match: int | None = None
    for item in skins.values() if isinstance(skins, dict) else []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "")
        skin_id = item.get("id")
        try:
            skin_id_int = int(skin_id)
        except (TypeError, ValueError):
            continue

        normalized_name = _normalize_skin_name(name)
        if normalized_name == wanted:
            exact_match = skin_id_int
            break
        if item.get("isBase") and normalized_name and normalized_name in wanted:
            base_match = skin_id_int

    return exact_match if exact_match is not None else base_match


def download_runeforge_mod(value: str, skin_id: int | None = None) -> RuneForgeDownloadResult:
    """Download a RuneForge mod into Aurelia custom mod storage."""
    source_url = normalize_runeforge_url(value)
    session = requests.Session()
    session.headers.update({"User-Agent": APP_USER_AGENT})

    log.info("[RuneForge] Fetching mod page: %s", source_url)
    response = session.get(source_url, timeout=DEFAULT_SKIN_DOWNLOAD_TIMEOUT_S)
    response.raise_for_status()

    title = _extract_title(response.text)
    skin_hint = _extract_skin_hint(response.text)
    asset_url = _extract_asset_url(response.text)
    _validate_asset_url(asset_url)

    inferred_skin_id = skin_id if skin_id is not None else _infer_skin_id_from_hint(session, skin_hint)

    storage = ModStorageService()
    target_dir, target_label = _target_directory(storage, inferred_skin_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    source_filename = _filename_from_asset_url(asset_url)
    extension = Path(source_filename).suffix
    base_name = str(inferred_skin_id) if inferred_skin_id is not None and target_label.startswith("skins/") else _safe_title(title)
    target_path = target_dir / f"{base_name}{extension}"
    if target_path.exists():
        target_path = target_dir / f"{base_name} - {quote(source_filename, safe='').replace('%', '')[:18]}{extension}"

    log.info("[RuneForge] Downloading artifact to: %s", target_path)
    with session.get(asset_url, stream=True, timeout=DEFAULT_SKIN_DOWNLOAD_TIMEOUT_S) as download:
        download.raise_for_status()
        with target_path.open("wb") as handle:
            for chunk in download.iter_content(chunk_size=1024 * 256):
                if chunk:
                    handle.write(chunk)

    description_path = target_path.with_suffix(".txt")
    description = [
        f"Source: {source_url}",
        f"RuneForge asset: {asset_url}",
    ]
    if skin_hint:
        description.append(f"Skin hint: {skin_hint}")
    description_path.write_text("\n".join(description) + "\n", encoding="utf-8")

    return RuneForgeDownloadResult(
        title=title,
        source_url=source_url,
        asset_url=asset_url,
        saved_path=target_path,
        target=target_label,
        skin_hint=skin_hint,
    )
