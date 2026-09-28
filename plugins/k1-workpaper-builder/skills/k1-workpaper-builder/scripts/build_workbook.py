#!/usr/bin/env python3
"""Compile per-K-1 JSON extractions (see references/extraction-schema.md) into an Excel workbook.

Usage:
  python3 build_workbook.py --data "/path/to/data" --out "/path/to/Name_K1_Summary.xlsx" \
                            [--title "Client Name — 2025 K-1 Summary"]

Reads every *.json in --data, splits 1065 vs 1120-S, discovers the union of box codes and states,
and writes: Read Me, 1065 K-1s, [1120S K-1s], State Income & Withholding, Box Code Legend.
"""
import json, glob, os, sys, argparse
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("openpyxl not installed. Run: pip3 install openpyxl")

# ---- form-type configuration --------------------------------------------------
CONFIG = {
    '1065': {
        'num': ['1','2','3','4a','4b','4c','5','6a','6b','6c','7','8','9a','9b','9c','10','12','14'],
        'coded': ['11','13','15','17','18','19','20','21'],
        'order': ['1','2','3','4a','4b','4c','5','6a','6b','6c','7','8','9a','9b','9c','10',
                  '11','12','13','14','15','16','17','18','19','20','21'],
        'k3_box': '16',
        'labels': {
            '1':'Ordinary business income (loss)','2':'Net rental RE income (loss)','3':'Other net rental income (loss)',
            '4a':'Guaranteed pmts services','4b':'Guaranteed pmts capital','4c':'Total guaranteed pmts',
            '5':'Interest income','6a':'Ordinary dividends','6b':'Qualified dividends','6c':'Dividend equivalents',
            '7':'Royalties','8':'Net ST capital gain (loss)','9a':'Net LT capital gain (loss)','9b':'Collectibles 28% gain',
            '9c':'Unrecap. §1250 gain','10':'Net §1231 gain (loss)','12':'Section 179 deduction','14':'Self-employment earnings',
        },
        'has_capital': True,
    },
    '1120S': {
        'num': ['1','2','3','4','5a','5b','6','7','8a','8b','8c','9','10','11'],
        'coded': ['12','13','15','16','17'],
        'order': ['1','2','3','4','5a','5b','6','7','8a','8b','8c','9','10','11',
                  '12','13','14','15','16','17'],
        'k3_box': '14',
        'labels': {
            '1':'Ordinary business income (loss)','2':'Net rental RE income (loss)','3':'Other net rental income (loss)',
            '4':'Interest income','5a':'Ordinary dividends','5b':'Qualified dividends','6':'Royalties',
            '7':'Net ST capital gain (loss)','8a':'Net LT capital gain (loss)','8b':'Collectibles 28% gain',
            '8c':'Unrecap. §1250 gain','9':'Net §1231 gain (loss)','10':'Other income (loss)','11':'Section 179 deduction',
        },
        'has_capital': False,
    },
}

# ---- styles -------------------------------------------------------------------
HEAD = Font(bold=True, color='FFFFFF', size=9)
HEADFILL = PatternFill('solid', fgColor='1F4E78')
CAPFILL = PatternFill('solid', fgColor='FFE699')
LIABFILL = PatternFill('solid', fgColor='F8CBAD')
TOTFILL = PatternFill('solid', fgColor='D9D9D9')
BAD = PatternFill('solid', fgColor='FFC7CE')
GOOD = PatternFill('solid', fgColor='C6EFCE')
_thin = Side(style='thin', color='BFBFBF')
BORDER = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)
NUMFMT = '#,##0;(#,##0)'


def money(v):
    return None if v in (None, '') else v


def norm_type(r):
    t = str(r.get('form_type', '')).replace('-', '').upper()
    return '1120S' if '1120' in t else '1065'


def discover_codes(recs, coded_boxes):
    cols = {b: [] for b in coded_boxes}
    for r in recs:
        for b in coded_boxes:
            for d in ((r.get('boxes') or {}).get(b) or {}).get('detail') or []:
                c = (d.get('code') or '').strip()
                if c and c not in cols[b]:
                    cols[b].append(c)
    return cols


def build_federal_sheet(ws, group, cfg):
    coded_cols = discover_codes(group, cfg['coded'])
    cols = [('entity_name', 'Issuing Entity', 'text'), ('entity_ein', 'EIN', 'text'),
            ('final_k1', 'Final K-1', 'flag')]
    for b in cfg['order']:
        if b in cfg['num']:
            cols.append((('box', b), f"Box {b}\n{cfg['labels'].get(b,'')}", 'num'))
        elif b == cfg['k3_box']:
            cols.append((('k3', b), f'Box {b}\nK-3 attached', 'flag'))
        elif b in cfg['coded']:
            codes = coded_cols.get(b, [])
            if not codes:
                cols.append((('box', b), f'Box {b}', 'num'))
            for c in codes:
                cols.append((('code', b, c), f'Box {b} — {c}', 'num'))
    if cfg['has_capital']:
        for k, h in [('beginning','Beg. capital account'),('contributed','Capital contributed'),
                     ('current_year_net_income','Current yr net income (loss)'),
                     ('other_increase_decrease','Other increase (decrease)'),
                     ('withdrawals_distributions','Withdrawals & distributions'),
                     ('ending','Ending capital account')]:
            cols.append((('cap', k), h, 'num'))
        cols.append((('cap_ties',), 'Capital ties?', 'ties'))
        for k, h in [('nonrecourse_beg','Nonrecourse (beg)'),('nonrecourse_end','Nonrecourse (end)'),
                     ('qualified_nonrecourse_beg','Qual. nonrecourse (beg)'),('qualified_nonrecourse_end','Qual. nonrecourse (end)'),
                     ('recourse_beg','Recourse (beg)'),('recourse_end','Recourse (end)')]:
            cols.append((('liab', k), h, 'num'))
    cols.append((('notes',), 'Notes', 'text'))

    for ci, (key, hdr, kind) in enumerate(cols, 1):
        c = ws.cell(1, ci, hdr)
        c.font = HEAD; c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        if isinstance(key, tuple) and key and key[0] == 'cap':
            c.fill = CAPFILL; c.font = Font(bold=True, size=9)
        elif isinstance(key, tuple) and key and key[0] == 'liab':
            c.fill = LIABFILL; c.font = Font(bold=True, size=9)
        else:
            c.fill = HEADFILL
    ws.freeze_panes = 'C2'; ws.row_dimensions[1].height = 42

    numeric_cols = []
    for ri, r in enumerate(group, 2):
        boxes = r.get('boxes') or {}; cap = r.get('capital_account') or {}; liab = r.get('liabilities') or {}
        for ci, (key, hdr, kind) in enumerate(cols, 1):
            val = None
            if key == 'entity_name': val = r.get('entity_name')
            elif key == 'entity_ein': val = r.get('entity_ein')
            elif key == 'final_k1': val = 'YES' if r.get('final_k1') else ''
            elif isinstance(key, tuple):
                if key[0] == 'box': val = money((boxes.get(key[1]) or {}).get('amount'))
                elif key[0] == 'k3': val = 'YES' if (boxes.get(key[1]) or {}).get('k3_attached') else ''
                elif key[0] == 'code':
                    for d in ((boxes.get(key[1]) or {}).get('detail') or []):
                        if (d.get('code') or '').strip() == key[2]:
                            val = money(d.get('amount')); break
                elif key[0] == 'cap': val = money(cap.get(key[1]))
                elif key[0] == 'liab': val = money(liab.get(key[1]))
                elif key[0] == 'notes': val = r.get('notes')
            c = ws.cell(ri, ci); c.border = BORDER
            if kind == 'num':
                c.value = val; c.number_format = NUMFMT
                if ci not in numeric_cols: numeric_cols.append(ci)
            elif kind == 'ties':
                ties = cap.get('ties'); comp = cap.get('computed_ending'); end = cap.get('ending')
                if ties is True: c.value = '✓ ties'; c.fill = GOOD
                elif ties is False:
                    diff = (comp or 0) - (end or 0) if (comp is not None and end is not None) else None
                    c.value = f'DIFF {diff:,.0f}' if diff is not None else 'CHECK'; c.fill = BAD
            else:
                c.value = val; c.alignment = Alignment(wrap_text=(key == ('notes',)), vertical='top')
    tr = 2 + len(group)
    ws.cell(tr, 1, 'TOTAL').font = Font(bold=True)
    for ci in range(1, len(cols) + 1):
        cc = ws.cell(tr, ci); cc.fill = TOTFILL; cc.border = BORDER
    for ci in numeric_cols:
        col = get_column_letter(ci)
        c = ws.cell(tr, ci, f'=SUM({col}2:{col}{tr-1})')
        c.number_format = NUMFMT; c.font = Font(bold=True); c.fill = TOTFILL; c.border = BORDER
    ws.cell(tr, 1, 'TOTAL').font = Font(bold=True)
    for ci, (key, hdr, kind) in enumerate(cols, 1):
        w = 12
        if key == 'entity_name': w = 34
        elif key == 'entity_ein': w = 12
        elif key == ('notes',): w = 50
        elif kind == 'num': w = 13
        ws.column_dimensions[get_column_letter(ci)].width = w


def build_state_sheet(ws, recs):
    states = []
    for r in recs:
        for s in (r.get('states') or []):
            st = (s.get('state') or '').strip().upper()
            if st and st not in states: states.append(st)
    states.sort()
    cols = ['Issuing Entity', 'Form']
    for st in states: cols += [f'{st} Income', f'{st} Withholding', f'{st} Composite?']
    for ci, h in enumerate(cols, 1):
        c = ws.cell(1, ci, h); c.font = HEAD; c.fill = HEADFILL; c.border = BORDER
        c.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
    ws.freeze_panes = 'B2'; ws.row_dimensions[1].height = 30
    numeric_cols = []
    for ri, r in enumerate(recs, 2):
        smap = {(s.get('state') or '').strip().upper(): s for s in (r.get('states') or [])}
        ws.cell(ri, 1, r.get('entity_name')).border = BORDER
        ws.cell(ri, 2, norm_type(r)).border = BORDER
        for i, st in enumerate(states):
            base = 3 + i * 3; s = smap.get(st)
            inc = ws.cell(ri, base, money(s.get('income')) if s else None)
            wh = ws.cell(ri, base + 1, money(s.get('withholding')) if s else None)
            comp = ws.cell(ri, base + 2)
            inc.number_format = NUMFMT; wh.number_format = NUMFMT
            inc.border = BORDER; wh.border = BORDER; comp.border = BORDER
            if base not in numeric_cols: numeric_cols += [base, base + 1]
            if s:
                cv = s.get('composite')
                comp.value = 'YES' if cv is True else ('No' if cv is False else '')
                if cv is True: comp.fill = GOOD
    tr = 2 + len(recs)
    ws.cell(tr, 1, 'TOTAL').font = Font(bold=True)
    for ci in numeric_cols:
        col = get_column_letter(ci)
        c = ws.cell(tr, ci, f'=SUM({col}2:{col}{tr-1})')
        c.number_format = NUMFMT; c.font = Font(bold=True); c.fill = TOTFILL; c.border = BORDER
    ws.column_dimensions['A'].width = 34; ws.column_dimensions['B'].width = 8
    for ci in range(3, len(cols) + 1): ws.column_dimensions[get_column_letter(ci)].width = 14


def build_legend_sheet(ws, recs, all_coded):
    lbl = {}
    for r in recs:
        for b, dlist in (r.get('boxes') or {}).items():
            for d in (dlist or {}).get('detail') or []:
                code = (d.get('code') or '').strip(); label = (d.get('label') or '').strip()
                if code and label:
                    key = (b, code)
                    if key not in lbl or len(label) > len(lbl[key]): lbl[key] = label
    for ci, h in enumerate(['Box', 'Code', 'Description (as reported in statements)'], 1):
        c = ws.cell(1, ci, h); c.font = HEAD; c.fill = HEADFILL; c.border = BORDER
    ri = 2
    for (b, code) in sorted(lbl.keys(), key=lambda x: (x[0], x[1])):
        ws.cell(ri, 1, f'Box {b}').border = BORDER
        ws.cell(ri, 2, code).border = BORDER
        ws.cell(ri, 3, lbl[(b, code)]).border = BORDER
        ri += 1
    ws.column_dimensions['A'].width = 10; ws.column_dimensions['B'].width = 8; ws.column_dimensions['C'].width = 80
    ws.freeze_panes = 'A2'


def build_readme(ws, recs, n1065, n1120, title):
    lines = [
        (title, 12, True), ('', 10, False),
        (f'Source: {len(recs)} Schedule K-1 tax package(s). {n1065} Form 1065 (partnership), {n1120} Form 1120-S (S-corp).', 10, False),
        ('', 10, False),
        ('SHEETS', 11, True),
        ('  • "1065 K-1s" / "1120S K-1s" — one row per K-1. Every populated Part III box; coded boxes are broken', 10, False),
        ('    into one column per code actually reported. 1065 sheet also carries the Section L capital account,', 10, False),
        ('    a "Capital ties?" check, and Section K liabilities. Bottom TOTAL row sums each numeric column.', 10, False),
        ('  • "State Income & Withholding" — one row per K-1, three columns per state (Income, Withholding, Composite?).', 10, False),
        ('  • "Box Code Legend" — description of each box/code column, taken from the K-1 footnote statements.', 10, False),
        ('', 10, False),
        ('VERIFICATION', 11, True),
        ('  • Capital account tie: Beginning + Contributed + Current-yr net income (loss) + Other − Withdrawals = Ending.', 10, False),
        ('  • Every "SEE STMT" reference was traced into the statements after page 1 and broken out per code.', 10, False),
        ('', 10, False),
        ('CAVEATS', 11, True),
        ('  • A Box 19-D style "deemed" distribution (a drop in liability share, not cash) is correctly excluded from', 10, False),
        ('    Section L withdrawals — see each row\'s Notes.', 10, False),
        ('  • Federal backup withholding is not state withholding and is not on the state sheet.', 10, False),
        ('  • Prepared by automated extraction. Spot-check against the source PDFs and consult a CPA before filing.', 10, False),
    ]
    for ri, (txt, sz, bold) in enumerate(lines, 1):
        c = ws.cell(ri, 1, txt); c.font = Font(bold=bold, size=sz)
        c.alignment = Alignment(vertical='top')
    ws.column_dimensions['A'].width = 125


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True, help='directory of per-K-1 *.json files')
    ap.add_argument('--out', required=True, help='output .xlsx path')
    ap.add_argument('--title', default='Schedule K-1 Summary')
    a = ap.parse_args()

    recs = []
    for fp in glob.glob(os.path.join(a.data, '*.json')):
        try:
            recs.append(json.load(open(fp)))
        except Exception as e:
            print('BAD JSON', fp, e)
    def sortkey(r):
        try: return int(str(r.get('file_num', 0)))
        except Exception: return 0
    recs.sort(key=sortkey)
    if not recs:
        sys.exit(f'No JSON found in {a.data}')

    r1065 = [r for r in recs if norm_type(r) == '1065']
    r1120 = [r for r in recs if norm_type(r) == '1120S']

    wb = Workbook()
    ws = wb.active; ws.title = 'Read Me'
    build_readme(ws, recs, len(r1065), len(r1120), a.title)
    if r1065:
        build_federal_sheet(wb.create_sheet('1065 K-1s'), r1065, CONFIG['1065'])
    if r1120:
        build_federal_sheet(wb.create_sheet('1120S K-1s'), r1120, CONFIG['1120S'])
    build_state_sheet(wb.create_sheet('State Income & Withholding'), recs)
    all_coded = set(CONFIG['1065']['coded']) | set(CONFIG['1120S']['coded'])
    build_legend_sheet(wb.create_sheet('Box Code Legend'), recs, all_coded)
    wb.save(a.out)
    print(f'WROTE {a.out}  |  1065={len(r1065)} 1120S={len(r1120)} total={len(recs)}')


if __name__ == '__main__':
    main()
