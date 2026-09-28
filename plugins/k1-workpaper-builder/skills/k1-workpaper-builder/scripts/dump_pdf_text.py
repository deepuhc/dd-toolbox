#!/usr/bin/env python3
"""Dump the text layer of PDF pages — good for reading K-1 statements / footnotes.

Usage:
  python3 dump_pdf_text.py "<file.pdf>" [range] [--shift N]

  range : 'all' (default), a single page '7', or a span '3-12'
  --shift N : decode a Caesar-shifted text layer by N (some issuers ship PDFs whose text is
              offset by a fixed amount, e.g. --shift 2; the rendered image always reads fine)
"""
import sys
try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF not installed. Run: pip3 install pymupdf")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    pdf = args[0]
    shift = 0
    rng = 'all'
    i = 1
    while i < len(args):
        if args[i] == '--shift':
            shift = int(args[i + 1]); i += 2
        else:
            rng = args[i]; i += 1
    doc = fitz.open(pdf)
    if rng == 'all':
        pages = range(1, doc.page_count + 1)
    elif '-' in rng:
        a, b = rng.split('-'); pages = range(int(a), int(b) + 1)
    else:
        pages = [int(rng)]

    def dec(t):
        if not shift:
            return t
        return ''.join(chr(ord(c) + shift) if 32 <= ord(c) <= 125 else c for c in t)

    for p in pages:
        if p < 1 or p > doc.page_count:
            continue
        print(f"\n===== PAGE {p} =====")
        print(dec(doc[p - 1].get_text()))


if __name__ == '__main__':
    main()
