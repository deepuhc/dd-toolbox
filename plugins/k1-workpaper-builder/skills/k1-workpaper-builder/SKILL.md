---
name: k1-workpaper-builder
description: >-
  Use when the user supplies one or more Schedule K-1 tax packages (Form 1065 partnership
  and/or Form 1120-S S-corporation PDFs) and wants them turned into a spreadsheet / workpaper —
  e.g. "build a spreadsheet for these K-1s", "summarize my K-1s", "tie out the capital accounts",
  "state withholding by entity". Extracts every Part III box (with per-code statement detail),
  the Section L capital account, Section K liabilities / shareholder basis, verifies the numbers
  tie, and produces a multi-sheet Excel workbook plus a state income/withholding/composite summary.
license: MIT
---

# K-1 Workpaper Builder

You are acting as a meticulous CPA preparing a tax workpaper. Accuracy is paramount — this is
real tax data. Never guess a number; read it from the source, and when a box says "SEE STMT",
go find the amount in the statements. Show your verification.

## What "done" looks like
A single Excel workbook (`<Name>_K1_Summary.xlsx`) with:
1. **Read Me** — scope, methodology, verification result, caveats.
2. **1065 K-1s** — one row per partnership K-1: entity, EIN, Final-K-1 flag, every Part III box
   (1–21) with coded boxes broken into one column per code, then the Section L capital account,
   a "Capital ties?" check column, and Section K liabilities. A TOTAL row sums numeric columns.
3. **1120S K-1s** — same idea for S-corp K-1s (boxes 1–17; no Section L/K — see notes), created
   only if any 1120-S K-1s are present.
4. **State Income & Withholding** — one row per K-1, three columns per state (Income, Withholding,
   Composite?), covering every state that appears.
5. **Box Code Legend** — plain-English description of each box/code column.

## Environment setup (do this first)
The K-1 form face is a fillable form: raw text extraction returns the labels and the values in
*separate* blocks, so linear text is ambiguous. The reliable method is to **render the form page
to an image and read it visually**. Statements/footnotes, by contrast, extract as clean text.

Check for Python + PyMuPDF; install if missing (no system poppler needed):
```
python3 -c "import fitz" 2>/dev/null || pip3 install pymupdf
python3 -c "import openpyxl" 2>/dev/null || pip3 install openpyxl
```
The bundled scripts live in this skill's `scripts/` directory. Set `SKILL_DIR` to that path.

## Workflow

### 1. Inventory & classify
List the PDFs. For each, find the K-1 **form face** page and the **form type**:
```
python3 "$SKILL_DIR/scripts/classify.py" "/path/to/folder"
```
This prints, per file: page count, the detected form-face page, and 1065 vs 1120-S. If a file
shows no form page, its text layer may be scanned or encoded — see "Tricky PDFs" below.

### 2. Extract each K-1 (render → read → trace statements)
For every K-1, follow `references/extraction-schema.md` exactly and write one JSON file per K-1 to
a working `data/` directory. For each K-1:
- Render the form-face page and **Read the image** to capture Part III boxes, Section L capital
  account, and Section K liabilities:
  `python3 "$SKILL_DIR/scripts/render_pdf.py" "<file.pdf>" <page>` → Read the printed PNG path.
- Amounts in (parentheses) are **negative**. A lettered code + amount (e.g. `13 AE 4,222`,
  `20 A 1,494`) goes in that box's code detail.
- Dump the statement pages and trace every "SEE STMT" and every multi-component box, plus all
  **state** income/withholding and any **composite / PTE / nonresident-withholding** language:
  `python3 "$SKILL_DIR/scripts/dump_pdf_text.py" "<file.pdf>" all`
- **Verify the capital account ties**: beginning + contributed + current-year net income (loss)
  + other increase/(decrease) − withdrawals & distributions = ending. Record `ties` and the
  computed ending. If it doesn't tie, check for a **deemed distribution** (a Box 19-D / basis
  distribution that is a drop in liability share, not cash — it is correctly *excluded* from
  Section L) before flagging a real discrepancy.

For large batches, dispatch several extraction subagents in parallel (each handling a few K-1s,
each writing JSON), then compile once. Keep the JSON schema identical across agents.

### 3. Compile the workbook
```
python3 "$SKILL_DIR/scripts/build_workbook.py" --data "/path/to/data" --out "/path/to/<Name>_K1_Summary.xlsx"
```
The compiler is data-driven: it discovers the union of box codes and states from the JSON, splits
1065 vs 1120-S automatically, adds tie-out and TOTAL rows, and writes all five sheets.

### 4. Independent re-check & report
Re-recompute every capital-account tie from the JSON (don't trust the printed "ending" alone),
report the pass/fail count, and summarize state withholding and composite filings. Spot-check a
few box values against the rendered images. Tell the user the workbook path and flag any K-1 that
did not tie, any Final K-1s, and any deemed distributions.

## Tricky PDFs
- **Encoded text layer** (garbled dump like `Dmpa jclb`): usually a fixed Caesar shift. The dump
  script supports `--shift N` to decode (e.g. `--shift 2`). The rendered image always reads fine.
- **Scanned / image-only** (empty text layer): render pages and read them visually; there is no
  text to dump.
- **Form face not on page 1**: cover letters, K-3, or state K-1s often precede it — trust the
  classifier's detected page, or render adjacent pages until you see Part I/II/III.

## Guardrails (CPA hygiene)
- Report only states with real source income, withholding, or a composite election — do not invent.
- Distinguish **federal** backup withholding (e.g. Box 15-O on a 1065) from **state** withholding.
- Keep client PII out of any shared artifact; the workbook is a workpaper, not a filing.
- State clearly that this is automated extraction requiring CPA review before filing.
