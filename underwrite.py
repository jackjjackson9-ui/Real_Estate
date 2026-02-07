"""Simple underwriting helpers for rental property deals."""

from __future__ import annotations


def amortized_monthly_payment(loan_amount: float, annual_interest_rate: float, term_years: int) -> float:
    """Calculate monthly principal+interest payment using standard amortization."""
    monthly_rate = annual_interest_rate / 12
    total_payments = term_years * 12

    if loan_amount <= 0:
        return 0.0
    if monthly_rate == 0:
        return loan_amount / total_payments

    factor = (1 + monthly_rate) ** total_payments
    return loan_amount * (monthly_rate * factor) / (factor - 1)


def underwrite_listing(listing: dict, config: dict) -> dict:
    """Compute NOI, cap rate, CoC and supporting values for one listing."""
    purchase_price = float(listing["purchase_price"])

    notes = []

    if "rent_estimate_monthly" in listing and listing["rent_estimate_monthly"] is not None:
        rent_monthly = float(listing["rent_estimate_monthly"])
    else:
        rent_monthly = (purchase_price * float(config["rent_to_price_ratio"])) / 12
        notes.append("rent estimated")

    if "property_taxes_annual" in listing and listing["property_taxes_annual"] is not None:
        taxes_annual = float(listing["property_taxes_annual"])
    else:
        taxes_annual = purchase_price * float(config["tax_rate"])
        notes.append("tax estimated")

    annual_rent = rent_monthly * 12
    vacancy_rate = float(config["vacancy_rate"])
    management_rate = float(config["management_rate"])
    maintenance_rate = float(config["maintenance_rate"])
    capex_rate = float(config["capex_rate"])
    insurance_annual = float(config["insurance_annual"])

    noi = (
        annual_rent * (1 - vacancy_rate)
        - annual_rent * (management_rate + maintenance_rate + capex_rate)
        - taxes_annual
        - insurance_annual
    )

    cap_rate = noi / purchase_price if purchase_price else 0.0

    down_payment_rate = float(config["down_payment_rate"])
    closing_cost_rate = float(config["closing_cost_rate"])
    interest_rate = float(config["interest_rate"])
    term_years = int(config["term_years"])

    loan_amount = purchase_price * (1 - down_payment_rate)
    monthly_payment = amortized_monthly_payment(loan_amount, interest_rate, term_years)
    annual_debt_service = monthly_payment * 12

    annual_cash_flow = noi - annual_debt_service
    cash_invested = (purchase_price * down_payment_rate) + (purchase_price * closing_cost_rate)
    coc = annual_cash_flow / cash_invested if cash_invested else 0.0

    return {
        "id": listing.get("id", ""),
        "address": listing.get("address", ""),
        "city": listing.get("city", ""),
        "state": listing.get("state", ""),
        "zip": listing.get("zip", ""),
        "purchase_price": round(purchase_price, 2),
        "rent_monthly_used": round(rent_monthly, 2),
        "noi": round(noi, 2),
        "cap_rate": round(cap_rate, 4),
        "coc": round(coc, 4),
        "notes": "; ".join(notes) if notes else "used listing rent/taxes"
    }
