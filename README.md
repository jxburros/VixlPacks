# VixlPacks

Content packs for [Vixl](https://github.com/jxburros/Vixl): large data that the engine downloads the first time a
feature needs it, so the Python package stays small. A pack holds no code that Vixl runs.

| Pack | What it is | Used by |
| --- | --- | --- |
| [`emojis/`](emojis/README.md) | VIXL Line emoji artwork: about 4,000 Unicode emojis adapted from OpenMoji and 100 VIXL originals, as SVG with editable `.vixl` masters | Text that contains emojis, `vixl emoji`, emoji pack exports |
| [`fonts/`](fonts/README.md) | Third-party fonts the builds and examples use (Press Start 2P, Space Mono), named like Vixl's font cache | VixlExamples builds |

## How Vixl uses a pack

Vixl pins each pack to a commit of this repository and to the file's SHA-256, then fetches
`https://raw.githubusercontent.com/jxburros/VixlPacks/<commit>/<path>` and refuses a file whose hash differs.
Changing a pack here changes nothing for users until Vixl's pin (`PACKS` in `src/vixl/packs.py`) is updated, and
releases already published keep working because they pin an older commit. Don't rewrite this repository's history.

Packs can also be installed from a local file, or downloads switched off, with `VIXL_PACK_DIR`, `VIXL_<NAME>_PACK`
and `VIXL_PACK_DOWNLOAD=off`; see the module's documentation in Vixl.

## Adding a pack

Give it a folder with a README, its licences, and the script that rebuilds it (builders may need Vixl installed).
Then add an entry to `PACKS` in Vixl.

## Licences

The repository's [`LICENSE`](LICENSE) (MIT) covers the build scripts. Each pack carries its own data licences in its
folder: the emoji artwork is [CC BY-SA 4.0](emojis/LICENSE.txt), Unicode data is under the
[Unicode licence](emojis/UNICODE-LICENSE.txt), and the fonts are under the SIL Open Font License
([`fonts/sources/`](fonts/sources/)).
