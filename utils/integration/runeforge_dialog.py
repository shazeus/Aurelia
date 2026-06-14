"""
Small Win32 dialog for downloading RuneForge mods into Aurelia.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
import tempfile
import threading
from typing import Optional

import requests

try:
    from PIL import Image  # type: ignore
except ImportError:  # pragma: no cover
    Image = None  # type: ignore

from config import APP_DISPLAY_NAME
from utils.core.logging import get_logger
from utils.core.paths import get_asset_path
from utils.download.runeforge_downloader import RuneForgeDownloadError, download_runeforge_mod
from utils.system.win32_base import (
    BS_DEFPUSHBUTTON,
    BS_PUSHBUTTON,
    SW_SHOWNORMAL,
    WS_CAPTION,
    WS_CHILD,
    WS_EX_APPWINDOW,
    WS_EX_CLIENTEDGE,
    WS_SYSMENU,
    WS_TABSTOP,
    WS_VISIBLE,
    Win32Window,
    init_common_controls,
    user32,
)

log = get_logger()

MB_OK = 0x00000000
MB_ICONINFORMATION = 0x00000040
MB_ICONERROR = 0x00000010
MB_TOPMOST = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080
ES_LEFT = 0x0000
ES_AUTOHSCROLL = 0x0080
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E


class RuneForgeDownloadWindow(Win32Window):
    URL_EDIT_ID = 4201
    SKIN_ID_EDIT_ID = 4202
    DOWNLOAD_ID = 4203
    CANCEL_ID = 4204

    def __init__(self) -> None:
        super().__init__(
            class_name="AureliaRuneForgeDialog",
            window_title="RuneForge Download",
            width=460,
            height=230,
            style=WS_CAPTION | WS_SYSMENU,
        )
        self.url_edit_hwnd: Optional[int] = None
        self.skin_id_edit_hwnd: Optional[int] = None
        self.url_result: Optional[str] = None
        self.skin_id_result: Optional[int] = None
        self._done = threading.Event()
        self._icon_temp_path: Optional[str] = None
        self._icon_source_path: Optional[str] = self._prepare_window_icon()
        init_common_controls()

    def _prepare_window_icon(self) -> Optional[str]:
        try:
            candidate = get_asset_path("tray_ready.png")
            if candidate.exists() and Image is not None:
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ico")
                tmp_path = tmp_file.name
                tmp_file.close()
                with Image.open(candidate) as img:
                    img.save(tmp_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
                self._icon_temp_path = tmp_path
                return tmp_path
        except Exception as exc:  # noqa: BLE001
            log.debug(f"[RuneForge] Failed to prepare dialog icon: {exc}")

        try:
            ico = get_asset_path("icon.ico")
            if ico.exists():
                return str(ico)
        except Exception:
            pass
        return None

    def _get_text(self, hwnd: Optional[int]) -> str:
        if not hwnd:
            return ""
        length = self.send_message(hwnd, WM_GETTEXTLENGTH, 0, 0)
        if length <= 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.send_message(hwnd, WM_GETTEXT, length + 1, ctypes.addressof(buffer))
        return buffer.value.strip()

    def on_create(self) -> Optional[int]:
        margin_x = 20
        y = 18
        content_width = self.width - (margin_x * 2)

        self.create_control(
            "STATIC",
            "RuneForge mod URL or mod id:",
            WS_CHILD | WS_VISIBLE,
            0,
            margin_x,
            y,
            content_width,
            20,
            4300,
        )
        self.url_edit_hwnd = self.create_control(
            "EDIT",
            "",
            WS_CHILD | WS_VISIBLE | WS_TABSTOP | ES_LEFT | ES_AUTOHSCROLL,
            WS_EX_CLIENTEDGE,
            margin_x,
            y + 24,
            content_width,
            24,
            self.URL_EDIT_ID,
        )

        self.create_control(
            "STATIC",
            "Target skin id (optional, e.g. 55000 for Katarina base):",
            WS_CHILD | WS_VISIBLE,
            0,
            margin_x,
            y + 64,
            content_width,
            20,
            4301,
        )
        self.skin_id_edit_hwnd = self.create_control(
            "EDIT",
            "",
            WS_CHILD | WS_VISIBLE | WS_TABSTOP | ES_LEFT | ES_AUTOHSCROLL,
            WS_EX_CLIENTEDGE,
            margin_x,
            y + 88,
            180,
            24,
            self.SKIN_ID_EDIT_ID,
        )

        self.create_control(
            "STATIC",
            "Without a skin id, the mod is saved under Others.",
            WS_CHILD | WS_VISIBLE,
            0,
            margin_x + 190,
            y + 91,
            content_width - 190,
            20,
            4302,
        )

        button_y = y + 136
        self.create_control(
            "BUTTON",
            "Download",
            WS_CHILD | WS_VISIBLE | WS_TABSTOP | BS_DEFPUSHBUTTON,
            0,
            margin_x + content_width - 190,
            button_y,
            90,
            28,
            self.DOWNLOAD_ID,
        )
        self.create_control(
            "BUTTON",
            "Cancel",
            WS_CHILD | WS_VISIBLE | WS_TABSTOP | BS_PUSHBUTTON,
            0,
            margin_x + content_width - 90,
            button_y,
            90,
            28,
            self.CANCEL_ID,
        )

        if self.hwnd:
            self.set_window_ex_styles(self.hwnd, add=WS_EX_TOOLWINDOW, remove=WS_EX_APPWINDOW)
            if self._icon_source_path:
                self.set_window_icon(self._icon_source_path)
        return 0

    def on_command(self, command_id: int, notification_code: int, control_hwnd) -> Optional[int]:
        if command_id == self.DOWNLOAD_ID and notification_code == 0:
            url_text = self._get_text(self.url_edit_hwnd)
            skin_text = self._get_text(self.skin_id_edit_hwnd)
            skin_id = None
            if skin_text:
                try:
                    skin_id = int(skin_text)
                except ValueError:
                    user32.MessageBoxW(
                        self.hwnd,
                        "Skin id must be a number.",
                        f"{APP_DISPLAY_NAME} RuneForge",
                        MB_OK | MB_ICONERROR | MB_TOPMOST,
                    )
                    return 0
            self.url_result = url_text
            self.skin_id_result = skin_id
            self._done.set()
            user32.DestroyWindow(self.hwnd)
            return 0
        if command_id == self.CANCEL_ID and notification_code == 0:
            self.url_result = None
            self.skin_id_result = None
            self._done.set()
            user32.DestroyWindow(self.hwnd)
            return 0
        return None

    def on_close(self) -> Optional[int]:
        self.url_result = None
        self.skin_id_result = None
        self._done.set()
        return super().on_close()

    def on_destroy(self) -> Optional[int]:
        if self._icon_temp_path:
            try:
                os.remove(self._icon_temp_path)
            except OSError:
                pass
            self._icon_temp_path = None
        user32.PostQuitMessage(0)
        return 0


def show_runeforge_download_dialog() -> None:
    """Show the RuneForge dialog and download the selected mod."""
    result_holder: dict[str, Optional[str | int]] = {"url": None, "skin_id": None}
    done_event = threading.Event()

    def dialog_thread() -> None:
        window: Optional[RuneForgeDownloadWindow] = None
        try:
            window = RuneForgeDownloadWindow()
            window.show_window(SW_SHOWNORMAL)

            msg = wintypes.MSG()
            while True:
                res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res <= 0:
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

            if window and window.url_result:
                result_holder["url"] = window.url_result
                result_holder["skin_id"] = window.skin_id_result
        finally:
            done_event.set()

    thread = threading.Thread(target=dialog_thread, daemon=True)
    thread.start()
    done_event.wait()

    url = result_holder["url"]
    if not isinstance(url, str) or not url.strip():
        return

    try:
        result = download_runeforge_mod(url, result_holder["skin_id"] if isinstance(result_holder["skin_id"], int) else None)
        message = (
            f"Downloaded: {result.title}\n\n"
            f"Saved to: {result.target}\n"
            f"{result.saved_path}"
        )
        if result.skin_hint:
            message += f"\n\nRuneForge skin hint: {result.skin_hint}"
        user32.MessageBoxW(None, message, f"{APP_DISPLAY_NAME} RuneForge", MB_OK | MB_ICONINFORMATION | MB_TOPMOST)
    except (RuneForgeDownloadError, requests.RequestException, OSError) as exc:
        log.error(f"[RuneForge] Download failed: {exc}")
        user32.MessageBoxW(
            None,
            f"RuneForge download failed:\n\n{exc}",
            f"{APP_DISPLAY_NAME} RuneForge",
            MB_OK | MB_ICONERROR | MB_TOPMOST,
        )
