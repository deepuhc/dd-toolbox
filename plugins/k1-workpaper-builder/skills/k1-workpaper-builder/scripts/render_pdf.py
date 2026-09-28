#!/usr/bin/env python3
"""Render PDF page(s) to PNG images for visual reading (the reliable way to read a K-1 form face).

Usage:
  python3 render_pdf.py "<file.pdf>" <page> [<page> ...] [--dpi 210] [--out DIR]

Prints the path of each PNG written. Read those images with your image-reading tool.
"""
import sys, os
try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF not installed. Run: pip3 install pymupdf")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    pdf = args[0]
    dpi = 210
    outdir = None
    pages = []
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--dpi':
            dpi = int(args[i + 1]); i += 2
        elif a == '--out':
            outdir = args[i + 1]; i += 2
        else:
            pages.append(int(a)); i += 1
    if not pages:
        sys.exit("Specify at least one page number.")
    if outdir is None:
        outdir = os.path.join(os.path.dirname(os.path.abspath(pdf)), '_k1_img')
    os.makedirs(outdir, exist_ok=True)
    doc = fitz.open(pdf)
    base = os.path.splitext(os.path.basename(pdf))[0]
    scale = dpi / 96.0
    mat = fitz.Matrix(scale, scale)
    for p in pages:
        if p < 1 or p > doc.page_count:
            print(f"skip: page {p} out of range (1..{doc.page_count})")
            continue
        pix = doc[p - 1].get_pixmap(matrix=mat)
        out = os.path.join(outdir, f"{base}__p{p}.png")
        pix.save(out)
        print(out)


if __name__ == '__main__':
    main()
