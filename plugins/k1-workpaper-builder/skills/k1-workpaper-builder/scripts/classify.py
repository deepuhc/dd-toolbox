#!/usr/bin/env python3
"""Inventory a folder of K-1 PDFs: page count, detected form-face page, and form type.

Usage: python3 classify.py "/path/to/folder"   (or one or more .pdf paths)
"""
import sys, os, glob, re
try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF not installed. Run: pip3 install pymupdf")


def decode_shift(t, n):
    return ''.join(chr(ord(c) + n) if 32 <= ord(c) <= 125 else c for c in t)


def alnum(text):
    # collapse to lowercase letters/digits only — robust to dropped spaces, control chars,
    # punctuation, and hyphens in encoded/reflowed text layers
    return re.sub(r'[^a-z0-9]', '', text.lower())


def looks_like_form(text):
    t = alnum(text)
    # "Schedule K-1" is often an image, so don't require it; anchor on Part III box labels
    return 'ordinarybusinessincome' in t and (
        'partiii' in t or 'currentyearincome' in t or 'form1065' in t or 'form1120s' in t)


def detect(path):
    doc = fitz.open(path)
    form_page, ftype = None, None
    for i in range(doc.page_count):
        raw = doc[i].get_text()
        text = raw
        if raw and not looks_like_form(raw):
            # try common encoded text layers (Caesar shift) before giving up
            for n in (2, 1, 3, -1, -2):
                d = decode_shift(raw, n)
                if looks_like_form(d):
                    text = d
                    break
        if looks_like_form(text):
            form_page = i + 1
            t = alnum(text)
            if 'form1120s' in t or 'form1120' in t:
                ftype = '1120S'
            elif 'form1065' in t:
                ftype = '1065'
            break
    empty = all(not doc[i].get_text().strip() for i in range(min(3, doc.page_count)))
    note = '' if form_page else ('scanned/image-only?' if empty else 'encoded or unusual layout')
    return doc.page_count, form_page, ftype, note


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    files = []
    for a in args:
        if os.path.isdir(a):
            files += sorted(glob.glob(os.path.join(a, '*.pdf')))
        else:
            files.append(a)
    if not files:
        sys.exit("No PDFs found.")
    print(f"{'pages':>5}  {'form_pg':>7}  {'type':<6}  file")
    for f in files:
        try:
            pages, fp, ft, note = detect(f)
            extra = f'   <-- {note}' if note else ''
            print(f"{pages:>5}  {str(fp):>7}  {str(ft):<6}  {os.path.basename(f)}{extra}")
        except Exception as e:
            print(f"    ?        ?  ?       {os.path.basename(f)}   ERROR: {e}")


if __name__ == '__main__':
    main()
