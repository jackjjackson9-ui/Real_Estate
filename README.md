# Real Estate Deal Underwriter (Minimal Python Prototype)

This is a tiny, beginner-friendly prototype that reads local sample property listings, underwrites each deal, writes a CSV file, and prints the top 5 deals by Cash-on-Cash return.

## What it does

- Reads config from `config.json`
- Reads listings from `data/sample_listings.json`
- Calculates for each listing:
  - NOI (Net Operating Income)
  - Cap Rate
  - Cash-on-Cash return (CoC)
- Saves all results to `output/deals.csv`
- Prints top 5 deals by CoC in the console

## Run it in Codex

From the repo root, run:

```bash
python -m unittest
python main.py
```

If successful, you will see top 5 deals printed and a new file at:

- `output/deals.csv`

## Run it locally (non-programmer version)

1. Install **Python 3** on your computer.
2. Open a terminal.
3. Go to the project folder.
4. Run:

```bash
python -m unittest
python main.py
```

Then open `output/deals.csv` in Excel, Google Sheets, or any spreadsheet tool.

## Edit assumptions (`config.json`)

Open `config.json` and change values like:

- `rent_to_price_ratio`
- `vacancy_rate`
- `management_rate`
- `maintenance_rate`
- `capex_rate`
- `tax_rate`
- `insurance_annual`
- `down_payment_rate`
- `interest_rate`
- `term_years`
- `closing_cost_rate`

All rates are decimal values. Example: `0.06` means 6%.

## Edit sample listings (`data/sample_listings.json`)

Each listing is a JSON object. Required fields for this prototype:

- `id`
- `address`
- `city`
- `state`
- `zip`
- `purchase_price`

Optional fields:

- `rent_estimate_monthly` (if missing, rent is estimated from config)
- `property_taxes_annual` (if missing, taxes are estimated from config)

## Formula summary (annualized)

- If rent missing:
  - `rent_monthly = (purchase_price * rent_to_price_ratio) / 12`
- Vacancy loss:
  - `annual_rent * vacancy_rate`
- Operating expenses:
  - `annual_rent * (management_rate + maintenance_rate + capex_rate)`
- Taxes:
  - Listing value if provided, otherwise `purchase_price * tax_rate`
- NOI:
  - `(rent*12)*(1-vacancy_rate) - (rent*12)*(management+maintenance+capex) - taxes - insurance`
- Cap rate:
  - `NOI / purchase_price`
- Loan amount:
  - `purchase_price * (1 - down_payment_rate)`
- Debt service:
  - monthly amortized P&I payment × 12
- Annual cash flow:
  - `NOI - annual_debt_service`
- Cash invested:
  - `down_payment + closing_cost_rate * purchase_price`
- CoC:
  - `annual_cash_flow / cash_invested`
