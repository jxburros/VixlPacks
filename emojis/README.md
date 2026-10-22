# VIXL Line emoji pack

`artwork.zip` holds the artwork Vixl draws for emojis in text: `svg/<key>.svg` for every entry and
`vixl/<key>.vixl` editable masters. Vixl keeps the small catalog (`src/vixl/data/emojis/catalog.json`)
in the engine and downloads this archive the first time it draws an emoji, then caches it in
`~/.cache/vixl/packs/`. See Vixl's [emoji guide](https://github.com/jxburros/Vixl/blob/main/docs/emojis.md)
for installing it ahead of time or offline.

Licenses: the Unicode artwork is adapted from OpenMoji and, with the 100 VIXL originals, is licensed under
[CC BY-SA 4.0](LICENSE.txt). Unicode data is under the [Unicode license](UNICODE-LICENSE.txt).

## Files

| Path | What it is |
| --- | --- |
| `artwork.zip` | The pack Vixl downloads |
| `sources/reactions/` | Source SVGs for the 100 VIXL originals (faces, reactions, everyday symbols) |
| `build_pack.py` | Rebuilds `artwork.zip` and `catalog.json` from OpenMoji, Unicode and `sources/` |
| `build_review_sheets.py` | Builds a review sheet and sample destination packs into `emojis/output/` |

## Updating the pack

1. Download the sources listed in Vixl's `docs/emojis.md`, then run, with Vixl installed:
   `python emojis/build_pack.py --sources /path/to/sources`
2. Copy the new `catalog.json` to Vixl's `src/vixl/data/emojis/`.
3. Commit `artwork.zip` here, then update the `emojis` entry in `PACKS` in Vixl's `src/vixl/packs.py`: the new
   commit, the new `sha256sum emojis/artwork.zip` and the size in bytes.
