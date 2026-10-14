# -*- coding: utf-8 -*-
"""Embed the blank form pages into index.html.

The PDFs in forms/ are Word's own export of the official forms (Word: Save As
PDF). Each page is rendered to a palette PNG and written into index.html
between the FORM-PAGES markers, where the app draws the day's data on top.

When a form gets a new edition: replace the .docx, export it to PDF again,
run this script, and check that the cell coordinates in F33 / F57 in
index.html still match (they are PDF points, measured from the export).

usage: python build/embed_forms.py
"""
import base64, io, os, re, sys

import pymupdf
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DPI = 200
COLORS = 128
FORMS = {"33.1": "form-33.1.pdf", "57": "form-57.pdf"}


def pages(pdf):
    out = []
    for p in pymupdf.open(pdf):
        pix = p.get_pixmap(dpi=DPI)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        im = im.quantize(COLORS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        b = io.BytesIO()
        im.save(b, "PNG", optimize=True)
        out.append("data:image/png;base64," + base64.b64encode(b.getvalue()).decode("ascii"))
    return out


def main():
    data = {k: pages(os.path.join(ROOT, "forms", f)) for k, f in FORMS.items()}
    body = ",\n".join(
        '"%s":[\n%s]' % (k, ",\n".join('"%s"' % s for s in v)) for k, v in data.items())
    block = "/*FORM-PAGES:BEGIN*/\nconst FORM_PAGES={\n%s};\n/*FORM-PAGES:END*/" % body

    path = os.path.join(ROOT, "index.html")
    html = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in html else "\n"
    pat = re.compile(r"/\*FORM-PAGES:BEGIN\*/.*?/\*FORM-PAGES:END\*/", re.S)
    if not pat.search(html):
        sys.exit("FORM-PAGES markers not found in index.html")
    html = pat.sub(lambda m: block.replace("\n", nl), html, count=1)
    io.open(path, "w", encoding="utf-8", newline="").write(html)

    for k, v in data.items():
        print("form %s: %d pages, %d KB" % (k, len(v), sum(len(s) for s in v) // 1024))
    print("index.html: %d KB" % (len(html.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
