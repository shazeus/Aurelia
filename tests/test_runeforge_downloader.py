from utils.download.runeforge_downloader import (
    _extract_asset_url,
    _extract_skin_hint,
    _extract_title,
    _infer_skin_id_from_hint,
    _target_directory,
    normalize_runeforge_url,
)


def test_normalize_runeforge_mod_id():
    assert (
        normalize_runeforge_url("4e169d0b-5933-4c96-a2c5-c7ca59538847")
        == "https://runeforge.dev/mods/4e169d0b-5933-4c96-a2c5-c7ca59538847"
    )


def test_extract_runeforge_page_metadata():
    html = """
    <html>
      <head><meta property="og:title" content="Goth Katarina | Runeforge"/></head>
      <body>
        <div>Skin: Base Katarina Skin Contact: Author</div>
        <script>
          window.__data=["assetUrl","https://r2-prod.runeforge.dev/mod_release_artifacts%2Fid%2Ffile.fantome?filename=file.fantome"];
        </script>
      </body>
    </html>
    """

    assert _extract_title(html) == "Goth Katarina"
    assert _extract_skin_hint(html) == "Base Katarina Skin"
    assert _extract_asset_url(html).endswith("file.fantome?filename=file.fantome")


def test_infer_skin_id_from_base_skin_hint():
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "55000": {"id": 55000, "isBase": True, "name": "Katarina"},
                "55001": {"id": 55001, "isBase": False, "name": "Mercenary Katarina"},
            }

    class Session:
        def get(self, *args, **kwargs):
            return Response()

    assert _infer_skin_id_from_hint(Session(), "Base Katarina Skin") == 55000


def test_skin_target_directory_uses_skin_cache(monkeypatch, tmp_path):
    class Storage:
        mods_root = tmp_path / "mods"
        CATEGORY_OTHERS = "others"

        def get_skin_dir(self, skin_id):
            return self.mods_root / "skins" / str(skin_id)

    monkeypatch.setattr("utils.download.runeforge_downloader.get_skins_dir", lambda: tmp_path / "skins")

    target_dir, label = _target_directory(Storage(), 55000)

    assert target_dir == tmp_path / "skins" / "55" / "55000"
    assert label == "skins/55/55000"
