---
description: Build a verified Excel workpaper from a folder of Schedule K-1 PDFs
argument-hint: [path-to-folder-of-K1-PDFs]
---

Use the **k1-workpaper-builder** skill to process the Schedule K-1 tax packages in:

$ARGUMENTS

Follow the skill's workflow end to end: classify each PDF (1065 vs 1120-S, locate the form face),
render each form face and read it, trace every "SEE STMT" and per-box detail through the statements
after page 1, capture state income/withholding/composite info, verify each capital account ties,
then compile the multi-sheet Excel workbook. Finish with the workbook path and a short exceptions
summary (anything that did not tie, Final K-1s, deemed distributions, state withholding/composite).

If no path was provided above, ask the user which folder holds the K-1 PDFs.
