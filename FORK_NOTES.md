# Aurelia Fork Notes

This fork keeps Aurelia's upstream runtime behavior intact and only carries fork-local packaging, documentation, and visible project-link customization.

## Fork-Specific Changes

- GitHub-facing links in the README, installer metadata, plugin metadata, and in-client settings panel point to `aurelia/Aurelia`.
- The launcher updater now checks `aurelia/Aurelia` releases by default.
- League Client UI surfaces now show the Aurelia identity in SettingsPanel, ChromaWheel, FormsWheel, Party Mode, and tray/update titles where safe.
- The updater release source can be overridden with `AURELIA_RELEASE_REPO` or `AURELIA_RELEASE_API` for testing/custom builds.
- Upstream support/community links are left unchanged unless this fork starts maintaining its own support channel.
- Runtime injection, loader, and asset-processing behavior are intentionally untouched by this fork customization pass.

## Maintenance Rules

- Keep fork-only branding changes separate from runtime logic changes.
- Prefer small commits that are easy to compare against upstream.
- Re-check upstream changes before editing League Client integration code.
