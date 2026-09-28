# Reusable prompt for the K-1 workpaper builder

Copy this, fill in the `<…>` fields, and paste it to Claude. It is a cleaned-up, unambiguous
version of a typical "build me a spreadsheet from these K-1s" request.

---

Build a verified Excel workpaper from the Schedule K-1 PDFs in `<folder path>`.

**Layout — one row per K-1, columns in this order:**
1. Issuing entity name, then EIN.
2. Every populated Part III box, in form order (Box 1, 2, 3, 4…). For any box whose statements
   report multiple income/loss/deduction items or lettered codes, add one extra column per
   code (e.g. `Box 20 — A`, `Box 20 — Z`) rather than cramming them into one cell.
3. After the boxes: beginning capital account, capital contributed, current-year net income
   (loss), other increase/(decrease), withdrawals & distributions, ending capital account.
4. Then Section K liabilities: nonrecourse, qualified nonrecourse, and recourse (beginning & ending).
5. A "Capital ties?" column showing whether the capital account rolls forward correctly.

**Separate the K-1s into categories:** one sheet for Form 1065 (partnership) K-1s and one for
Form 1120-S (S-corp) K-1s, if any.

**Read past page 1.** Go through the statements/footnotes after the K-1 form face and make sure
every "SEE STMT" amount and every additional per-box item is captured.

**Verify the math ties** — recompute each capital account (beginning + contributions + current-year
income − withdrawals = ending) and flag anything that doesn't tie, plus any Final K-1s.

**Second workbook sheet — state income & tax withholding:** columns per state for state-source
income and any state withholding, plus a column flagging whether the entity filed a composite /
pass-through-entity return that included me. Show only states with real income, withholding, or a
composite election.

Tell me where the file is saved and give me a short summary of anything that needs my attention.

---

### Why this version is better than an off-the-cuff request
- **Removes ambiguity** about rows vs columns ("one row per K-1" is stated explicitly).
- **Names the exact column order and the capital-account roll-forward formula**, so the tie-out is
  unambiguous and checkable.
- **Splits 1065 vs 1120-S up front** instead of "if any".
- **Separates the state summary into its own deliverable** with income, withholding, and composite.
- **Asks for an exceptions summary** (didn't-tie / Final K-1) so you review the right things first.
