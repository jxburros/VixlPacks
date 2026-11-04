"""Render specimens/overview.png: every Vixl Original's name and a sample line, straight from the built TTFs."""

from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_originals import SOURCES, SPECIMENS, STYLES, style_of  # noqa: E402

ROW, WIDTH = 118, 2200


def main():
    styles = [style_of(s) for s in STYLES]
    image = Image.new("RGB", (WIDTH, 40 + ROW * len(styles)), "white")
    draw = ImageDraw.Draw(image)
    for i, st in enumerate(styles):
        y = 30 + i * ROW
        font = ImageFont.truetype(str(SOURCES / st["file"]), 64)
        draw.text((40, y), st["family"].replace("Vixl ", ""), font=font, fill="#111111")
        draw.text((620, y), "Jumpy quartz glyphs vex 2048!", font=font, fill="#111111")
        draw.line((40, y + ROW - 14, WIDTH - 40, y + ROW - 14), fill="#e4e4e4", width=2)
    SPECIMENS.mkdir(exist_ok=True)
    image.save(SPECIMENS / "overview.png", optimize=True)


if __name__ == "__main__":
    main()
