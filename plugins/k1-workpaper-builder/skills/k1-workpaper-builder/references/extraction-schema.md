# Per-K-1 JSON extraction schema

Write **one JSON file per K-1** into a working `data/` directory (e.g. `data/34.json`). Keep the
shape identical across every K-1 so `build_workbook.py` can compile them. Amounts are numbers
(no commas, no `$`); losses/parentheses are **negative**; unknown numerics are `null`, not `0`.

```json
{
  "file_num": "34",
  "entity_name": "VistaOne, L.P.",
  "entity_ein": "33-1386882",
  "form_type": "1065",
  "final_k1": false,
  "boxes": {
    "6a": {"amount": 1494},
    "11": {"amount": null, "detail": [{"code": "A", "label": "Other portfolio income", "amount": 123}]},
    "13": {"amount": 4222, "detail": [{"code": "AE", "label": "Portfolio deductions - investment expenses", "amount": 4222}]},
    "16": {"k3_attached": true},
    "19": {"detail": [{"code": "A", "label": "Cash & marketable securities", "amount": null}]},
    "20": {"detail": [{"code": "A", "label": "Investment income", "amount": 1494},
                       {"code": "Y", "label": "Net investment income", "amount": null}]},
    "21": {"amount": null}
  },
  "capital_account": {
    "beginning": 0, "contributed": 125000, "current_year_net_income": -2728,
    "other_increase_decrease": null, "withdrawals_distributions": 0, "ending": 122272,
    "ties": true, "computed_ending": 122272
  },
  "liabilities": {
    "nonrecourse_beg": null, "nonrecourse_end": 7969,
    "qualified_nonrecourse_beg": null, "qualified_nonrecourse_end": null,
    "recourse_beg": null, "recourse_end": null
  },
  "states": [
    {"state": "CA", "income": 4433, "withholding": 369, "composite": false, "notes": "592-B nonresident wh"}
  ],
  "notes": "Anything notable, ambiguous, or that did not tie."
}
```

## Rules
- **`boxes`**: include only populated boxes. Numeric boxes (1–12 on a 1065; 1–11 on an 1120-S) use
  `{"amount": n}`. Coded boxes use `{"amount": faceAmountOrNull, "detail": [{code,label,amount}, …]}`.
  Pull each coded amount from the statement when the face says "SEE STMT".
- **`form_type`**: `"1065"` or `"1120S"`.
- **`capital_account`** (1065): read Section L. Compute `computed_ending` and set `ties`. For 1120-S
  there is no Section L on the K-1 face — leave `capital_account`/`liabilities` out or null and note
  stock/debt basis in `notes` if provided.
- **`liabilities`** (1065): Section K — nonrecourse / qualified nonrecourse / recourse, beg & end.
- **`states`**: only where there is real state-source income, withholding, or a composite/PTE
  election. `composite: true` where the entity included this owner in a composite/PTE filing.
  Do **not** confuse federal backup withholding (e.g. 1065 Box 15-O) with state withholding.

## Box-16 / Box-14 (Schedule K-3)
On a 1065, Box 16 is the "Schedule K-3 is attached if checked" flag → `boxes."16".k3_attached`.
On an 1120-S, that flag is Box 14 → `boxes."14".k3_attached`.
