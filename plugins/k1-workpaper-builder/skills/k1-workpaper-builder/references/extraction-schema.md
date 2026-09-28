# Per-K-1 JSON extraction schema

Write **one JSON file per K-1** into a working `data/` directory (e.g. `data/34.json`). Keep the
shape identical across every K-1 so `build_workbook.py` can compile them. Amounts are numbers
(no commas, no `$`); losses/parentheses are **negative**; unknown numerics are `null`, not `0`.

The values below are a **fictional illustration** of the shape only — use the real numbers you read
from each K-1.

```json
{
  "file_num": "01",
  "entity_name": "Example Partners Fund, LP",
  "entity_ein": "00-0000000",
  "form_type": "1065",
  "final_k1": false,
  "boxes": {
    "6a": {"amount": 1000},
    "11": {"amount": null, "detail": [{"code": "A", "label": "Other portfolio income", "amount": 100}]},
    "13": {"amount": 500, "detail": [{"code": "AE", "label": "Portfolio deductions - investment expenses", "amount": 500}]},
    "16": {"k3_attached": true},
    "19": {"detail": [{"code": "A", "label": "Cash & marketable securities", "amount": null}]},
    "20": {"detail": [{"code": "A", "label": "Investment income", "amount": 1000},
                       {"code": "Y", "label": "Net investment income", "amount": null}]},
    "21": {"amount": null}
  },
  "capital_account": {
    "beginning": 10000, "contributed": 5000, "current_year_net_income": -500,
    "other_increase_decrease": null, "withdrawals_distributions": 2000, "ending": 12500,
    "ties": true, "computed_ending": 12500
  },
  "liabilities": {
    "nonrecourse_beg": null, "nonrecourse_end": 3000,
    "qualified_nonrecourse_beg": null, "qualified_nonrecourse_end": null,
    "recourse_beg": null, "recourse_end": null
  },
  "states": [
    {"state": "XX", "income": 1200, "withholding": 60, "composite": false, "notes": "nonresident withholding (e.g. CA 592-B)"}
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
