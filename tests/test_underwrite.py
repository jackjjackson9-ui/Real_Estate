import unittest

from underwrite import amortized_monthly_payment, underwrite_listing


class TestUnderwrite(unittest.TestCase):
    def setUp(self):
        self.config = {
            "rent_to_price_ratio": 0.009,
            "vacancy_rate": 0.06,
            "management_rate": 0.08,
            "maintenance_rate": 0.07,
            "capex_rate": 0.05,
            "tax_rate": 0.012,
            "insurance_annual": 1200,
            "down_payment_rate": 0.25,
            "interest_rate": 0.0675,
            "term_years": 30,
            "closing_cost_rate": 0.03,
        }

    def test_amortized_monthly_payment_positive(self):
        payment = amortized_monthly_payment(150000, 0.06, 30)
        self.assertGreater(payment, 0)

    def test_underwrite_uses_estimates_when_missing(self):
        listing = {
            "id": "T001",
            "address": "1 Test St",
            "city": "Testville",
            "state": "TS",
            "zip": "00000",
            "purchase_price": 200000,
        }
        result = underwrite_listing(listing, self.config)

        self.assertIn("rent estimated", result["notes"])
        self.assertIn("tax estimated", result["notes"])
        self.assertIn("coc", result)
        self.assertIn("noi", result)

    def test_underwrite_uses_provided_values(self):
        listing = {
            "id": "T002",
            "address": "2 Test St",
            "city": "Testville",
            "state": "TS",
            "zip": "00000",
            "purchase_price": 200000,
            "rent_estimate_monthly": 1900,
            "property_taxes_annual": 2500,
        }
        result = underwrite_listing(listing, self.config)

        self.assertEqual(result["notes"], "used listing rent/taxes")
        self.assertAlmostEqual(result["rent_monthly_used"], 1900.0)


if __name__ == "__main__":
    unittest.main()
