---
name: 401k-wire-transfer-testing
description: >-
  Use for a 401(k) / employee benefit plan audit when the user wants WP 5220 (or any "wire transfer",
  "timely remittance", "deferral remittance" or "payroll vs. trustee") testing done: match every
  payroll check date's 401(k) pre-tax, Roth, loan repayment and employer match withholdings (from
  payroll registers) to the recordkeeper/trustee contribution report, compute business days from check
  date to funding, and show over/(under) funding. Works with any payroll provider (ADP, Paychex,
  Paylocity, Gusto, UKG, Paycom...) and any recordkeeper (ADP Retirement, Fidelity, Empower, Principal,
  John Hancock, Vanguard, Ascensus...). Also invoked as /5220.
license: MIT
---

# 401(k) Wire Transfer / Timely Remittance Testing (WP 5220)

Use this skill for a benefit plan audit when you need to show that every payroll's 401(k) withholdings
reached the trustee/recordkeeper in the right amount and on time. It works for any payroll provider
and any recordkeeper or trustee.

**Deliverable:** one Excel workpaper in the standard layout below. Save it as a NEW file next to the
client's template, named `<template name> - <plan year> Completed.xlsx`. Never overwrite the template,
which is often open in Excel.

Accuracy matters: this is audit evidence. Never guess a number or a code mapping. Every total must tie
to a source report, and every difference must be explained.

## 1. Gather inputs
Ask only for what you can't find:
- **Payroll reports for the plan year.** Prefer one payroll register per pay run. Also take a year-end
  YTD report (e.g. ADP Master Control, Paychex Payroll Journal YTD, a deduction register).
- **The recordkeeper's contribution report** for the plan year (Schedule of Contributions,
  Contribution Detail, Remittance History, Deposit Report).
- If you can get them: a **loan repayment report**, and the **next year's contribution report**
  (needed for the last payroll of the year).
- **Plan details:**
  - Plan name, plan year, and roughly how many participants.
  - Which deduction codes are pre-tax 401(k), Roth, loan(s) and employer match. Also check for a
    non-elective/safe harbor contribution remitted per payroll.
- **The client template**, which is used only for tickmark wording and the WP reference.

If the files are on the user's computer, request access to the folder, then list it. Stage only the
PDFs or Excel files you need. Extract each PDF with `pdftotext -layout`. Read Excel/CSV exports
directly; prefer them over PDFs when the provider offers them. Scanned (image-only) PDFs need OCR
first, so tell the user and ask for a text-based export if one exists.

## 2. Map the codes for this provider (do this first, every client)
Payroll providers label things differently, so build a code map before parsing anything:
1. Open one full payroll register. Find the **company / grand totals** section (usually the last page
   of each run).
2. List every deduction and memo label it contains. Map each one to: 401(k) pre-tax, Roth, Loan
   (there may be several), ER Match, Eligible comp. Ignore taxes, garnishments, direct deposits and
   other benefits.
3. Write the map down in the workpaper notes, e.g.
   `K 401K = pre-tax; RTH ROTH = Roth; R KLOAN1 + 42 KLOAN2 = loans; memo K KMATCH = match`.
4. If a label is ambiguous, ask the user. Never guess.

Provider-specific parsing tips:
- **ADP (Workforce Now / RUN):**
  - Each run has a `Payroll Register` and an `ADP Master Control`.
  - Totals are in the block that starts at the last `COMPANY CODE` line and runs to `NET PAYROLL:`.
    Within it, `MEMO ANALYSIS` holds the match and comp, and `VOLUNTARY DED ANALYSIS` holds 401K, ROTH
    and loans.
  - Amounts use a space before the cents (`22 320 81` = 22,320.81), and a trailing `-` means negative.
  - The header line holds `Batch`, `Period Ending`, `Week` and `Pay Date`.
  - The file name pattern is `<co>_<YYYY-WW-N-batch>_Payroll_Register_*.pdf`.
  - Find the Master Control YTD accumulators on its company-totals page (e.g. `CA 401K YTD`,
    `CC Roth YTD`, a match YTD accumulator, `Y 401K`). Read the accumulator definitions near the front
    of the report to confirm which number is which.
- **Other providers:** look for a "Company Totals", "Deduction Summary" or "Payroll Summary" page.
  Employer match is often a memo or "employer contribution" line rather than a deduction. If there is
  no totals page, sum the employee-level detail per run, and rely even more on the tie to YTD.
- **Recordkeeper reports:**
  - You need, for each line: the **check/payroll date**, the **trade/deposit/funding date**, the
    source (Before-Tax, Roth, Match/QACA/Safe Harbor, Loan Repayment) and the amount.
  - Some reports show only one of the two dates. If so, say so and ask for a report that has both.
  - Exclude non-payroll lines and list them as reconciling items: rollovers, forfeitures applied,
    true-ups, transfers, fees.

## 3. Parse and aggregate (Python)
- **Payroll:** for each run, capture pay date, batch/run id, # of pays, 401(k), Roth, Loan (sum of all
  loan codes), Match and Eligible comp.
- **Group by check date.**
  - Combine runs that share a check date (off-cycle runs). Recordkeepers group by check date.
  - Each distinct check date is its own row, including small off-cycle dates.
  - Do not add monthly or quarterly subtotal rows.
- **Trustee:** for each check date, capture the trade date and the amount by source.
  - Assert there is only one trade date per check date. If there are several (split deposits), list
    every date in comments and use the latest one for the days calculation.
- **Payroll completeness checks:**
  - Sum the registers and compare the result to the year-end YTD report for each code. The difference
    must be 0.
  - If a run is missing, derive its amounts as YTD at the next run minus that run's register.
    Tickmark it `A1` and explain. Loans usually have no YTD accumulator, so flag them as unavailable.
  - Roll the YTD forward run by run where YTD reports exist for every run.
- **Cut-off at year end (use the pay date, i.e. the W-2 basis):**
  - Exclude pay dates in the next year, even if the work period ended in the plan year. Mention them
    in the notes.
  - The last payroll(s) of the plan year are often funded the next January. Show them with trustee
    status `Open`, back them out in an "Adjusted Totals" line, and request the next year's contribution
    report to confirm the funding date.

## 4. Workpaper layout (standard, one sheet named `5220` or the client's WP #)
Row 1 holds the title (client, plan, plan #, year, WP). Row 2 holds the sources. Row 4 holds the group
headers (shaded: payroll blue, trustee green, differences orange). Row 5 holds the column headers.
Data starts at row 6, and panes are frozen at C6.

| Cols | Content |
|---|---|
| A | Check date |
| B | Pay run(s) / batch |
| C | Tick |
| D | EE 401(k) pre-tax |
| E | Tick |
| F | EE Roth |
| G | Tick |
| H | ER Match |
| I | Tick |
| J | EE 401(k) loan |
| K | Tick |
| L | PR Total `=SUM(D,F,H,J)` |
| M | Trustee funding (trade) date |
| N | Tick |
| O | Check date per trustee |
| P | Tick |
| Q | EE 401(k) |
| R | Tick |
| S | Roth |
| T | Tick |
| U | Match |
| V | Tick |
| W | Loan |
| X | Tick |
| Y | Trustee Total `=SUM(Q,S,U,W)` |
| Z | Tick |
| AA | Business days `=NETWORKDAYS(A+1, M, Holidays)` |
| AB | Tick `=IF(AA<=$AL$5,"C","X")` |
| AC–AG | Trustee less payroll for 401k, Roth, Match, Loan, Total |
| AH | Timely? (`Yes` / `No` / `Open` / `N/A`) |
| AI | Comments |
| AK/AL | Inputs: timely threshold (default **7** business days) in AL5, and the bank holiday list from AL7 down |

If the plan has a per-payroll non-elective or safe harbor contribution, add it as an extra source pair
after Match in both sections and in the differences.

**Business days:** use `NETWORKDAYS(check date + 1, trade date, holidays)`. This counts business days
after the check date and handles a check date that falls on a holiday. Do not use
`NETWORKDAYS(...)-1`. Put the Federal Reserve bank holidays for the plan year and the following New
Year's Day in the holiday list.

**Below the data:**
1. A TOTALS row, with `=` footing ticks.
2. Payroll report totals (the YTD report), a check row (= 0), "Less: last payroll(s) funded in next
   year", and Adjusted Totals.
3. Trustee tie-out: report grand total less non-payroll items (rollovers, forfeitures, etc.) = the
   Trustee Total column. Also show the report's own subtotals (participant / employer).
4. Payroll vs Trustee vs Financials: EE 401k + Roth, Match, Total. Leave Financials as a blue input
   cell ("enter from WP 6150").
5. Timeliness summary (COUNTIF formulas): dates tested, timely, late, open, average and max business
   days.
6. Tickmark legend:
   - A = agreed to payroll register
   - A1 = derived from YTD / prior-year register
   - B = agreed to trustee report (amount, check date, trade date)
   - C = timely
   - X = non-timely
   - G = calculated difference
   - = = footed
7. Numbered notes: the code map, missing runs, cut-off, loans, non-payroll trustee items, and the
   threshold basis.

**Formatting:** Arial 9. Blue font for hard-coded source numbers, black for formulas, red bold for
tickmarks. Use accounting number format and `mm/dd/yyyy` dates. Use only formulas for totals and
differences, never hard-coded results. Recalculate (e.g. LibreOffice headless, or the xlsx skill's
`recalc.py` if available) and confirm 0 formula errors.

## 5. Known issues to flag every time
- **Loans:** many recordkeeper contribution schedules (including ADP's Schedule of Contributions) do
  not show loan repayments, so the loan column shows as under-funded. Note it and request the loan
  repayment / transaction history rather than calling it an exception.
- **Missing pay runs** in the archive: derive from YTD and request the register.
- **Year-end adjustment / true-up batches**, such as large deferral true-ups, S-corp 2% shareholder
  fringe, or 0-pay adjustment runs. Flag them for 402(g) / catch-up limit and deposit-timing review.
- **Runs with eligible comp but no deferral or match:** ask the user to confirm the plan's
  compensation definition.
- **Check-date mismatches** (e.g. trustee shows 01/01 when the payroll was 01/03): use the trustee
  check date for matching, but explain it.
- **Timeliness benchmark:** 7 business days is the DOL safe harbor for plans with fewer than 100
  participants (29 CFR 2510.3-102(a)(2)). Larger plans must remit as soon as amounts can reasonably be
  segregated, so treat 7 days as a benchmark and mention that in the notes. Any `No` row is a
  potential late remittance. Quantify it and suggest a lost-earnings / VFCP review.

## 6. Verify before delivering
- Payroll totals = the YTD report for each code (difference 0).
- The trustee column totals plus excluded non-payroll items = the report grand total. The report's
  participant and employer subtotals tie.
- Every trustee check date matched a payroll row, so no trustee date is left unmatched (assert this in
  code).
- After the cut-off adjustment, payroll vs trustee for EE (401k + Roth) and Match is 0, or every
  difference is explained in comments.
- 0 formula errors after recalculating.

## 7. Report back (brief)
Say where the file was saved. Then give:
- The number of check dates tested, how many were timely or late, and the average and max business
  days.
- Total funded (EE / ER).
- Each difference and its cause: next-year funding, loans not reported, missing runs, non-payroll
  items.
- What is still needed: the next year's contribution report, the loan history, missing registers, and
  the financials figure.

## Guardrails
- Never commit or share client data; outputs stay in the client's folder.
- Examples in this skill are illustrative only.
