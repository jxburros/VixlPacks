# Fonts pack

Third-party fonts that Vixl's builds and examples use, kept in one pinned archive instead of being committed next to
each project.

| Family | Weight | Licence |
| --- | --- | --- |
| Press Start 2P | 400 | [SIL OFL 1.1](sources/OFL-press-start-2p.txt) |
| Space Mono | 400 | [SIL OFL 1.1](sources/OFL-space-mono.txt) |

`fonts.zip` holds the `.ttf` files, their licences and `manifest.json`. The files are named the way Vixl's font cache
names them (`press-start-2p-400.ttf`), so unpacking the archive into `VIXL_FONT_CACHE` is all it takes for Vixl to use
them without a download.

Vixl's own fallback fonts (Noto and DejaVu) are not here: they ship inside the Vixl package so text renders offline.

## Use it

```python
import zipfile
from vixl import packs

with zipfile.ZipFile(packs.path("fonts")) as archive:   # downloads once, checks the pinned SHA-256
    archive.extractall("my-font-cache")                  # then set VIXL_FONT_CACHE=my-font-cache
```

## Update it

Put the font file in `sources/` with its licence, add it to `manifest.json`, run `python fonts/build_pack.py`, commit,
then update the `fonts` entry in `PACKS` in Vixl's `src/vixl/packs.py` (commit, sha256, bytes).
