# -*- coding: utf-8 -*-
"""Build the app icons from the company logo.

icons/source-logo.png is the Vasa Ecology logo (white background). Every icon
is the logo centred on a white square:
  - "any" icons fill ~84% of the square
  - the maskable icon keeps the logo inside the 80% safe-zone circle, because
    Android may crop it to a circle or a squircle
  - the apple-touch-icon has no transparency (iOS fills it with black)

usage: python build/make_icons.py
"""
import math, os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, "icons")


def icon(logo, size, fill):
    """logo scaled so its box takes `fill` of the square, centred on white"""
    sc = fill * size / max(logo.width, logo.height)
    w, h = round(logo.width * sc), round(logo.height * sc)
    out = Image.new("RGB", (size, size), "white")
    out.paste(logo.resize((w, h), Image.LANCZOS), ((size - w) // 2, (size - h) // 2))
    return out


def maskable(logo, size):
    """the logo's corners must stay inside a circle of 40% radius"""
    r = 0.40 * size
    diag = math.hypot(logo.width, logo.height)
    fill = 2 * r / diag * max(logo.width, logo.height) / size * 0.97
    return icon(logo, size, fill)


def main():
    logo = Image.open(os.path.join(ICONS, "source-logo.png")).convert("RGB")
    out = {
        "apple-touch-icon.png": icon(logo, 180, 0.82),
        "icon-192.png": icon(logo, 192, 0.84),
        "icon-512.png": icon(logo, 512, 0.84),
        "icon-maskable-512.png": maskable(logo, 512),
        "favicon-32.png": icon(logo, 32, 0.96),
    }
    for name, im in out.items():
        im.save(os.path.join(ICONS, name), "PNG", optimize=True)
        print("%-24s %dx%d" % (name, im.width, im.height))


if __name__ == "__main__":
    main()
