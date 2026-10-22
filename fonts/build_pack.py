"""Build fonts.zip from sources/ and manifest.json. Standard library only; the output is reproducible.

Usage, from the root of this repository:
    python fonts/build_pack.py

Prints the SHA-256 and size to put in the `fonts` entry of PACKS in Vixl's src/vixl/packs.py.
"""

import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
EPOCH = (2026, 1, 1, 0, 0, 0)  # fixed timestamps keep the zip, and so its pinned hash, stable


def build(output=HERE / "fonts.zip"):
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    names = {"manifest.json"}
    for font in manifest["fonts"]:
        names |= {font["file"], font["license"]}
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(names):
            source = HERE / name if name == "manifest.json" else HERE / "sources" / name
            info = zipfile.ZipInfo(name, EPOCH)
            info.compress_type, info.external_attr = zipfile.ZIP_DEFLATED, 0o644 << 16
            archive.writestr(info, source.read_bytes())
    data = Path(output).read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


if __name__ == "__main__":
    digest, size = build()
    print(f"fonts.zip  sha256 {digest}  bytes {size}")
