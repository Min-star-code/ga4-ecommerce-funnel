"""Consistency checks on the saved BigQuery results. Run: python -m unittest discover tests"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import analysis  # noqa: E402


def raw(name):
    return json.loads((ROOT / "data" / f"{name}.json").read_text())


class TestResults(unittest.TestCase):
    def test_revenue_matches_across_queries(self):
        monthly = sum(float(r["revenue_usd"]) for r in raw("monthly_overview"))
        by_medium = sum(float(r["revenue_usd"]) for r in raw("traffic_medium"))
        by_device = sum(float(r["revenue_usd"]) for r in raw("device"))
        self.assertAlmostEqual(monthly, by_medium, delta=5)   # medium totals are rounded to dollars
        self.assertAlmostEqual(monthly, by_device, delta=5)

    def test_users_match_across_queries(self):
        total = int(raw("purchase_funnel")[0]["all_users"])
        self.assertEqual(total, int(raw("data_quality")[0]["users"]))
        # each user is assigned one medium (from their earliest event), so medium groups add up to all users
        self.assertEqual(total, sum(int(r["users"]) for r in raw("traffic_medium")))
        # a user can use more than one device, so device groups add up to at least all users
        self.assertGreaterEqual(sum(int(r["users"]) for r in raw("device")), total)

    def test_purchasers_match(self):
        purchasers = int(raw("purchase_funnel")[0]["purchase"])
        self.assertEqual(purchasers, sum(int(r["purchasers"]) for r in raw("traffic_medium")))

    def test_funnel_never_grows(self):
        table, _ = analysis.funnel_table()
        users = list(table["users"])
        self.assertEqual(users, sorted(users, reverse=True))

    def test_rates_are_percentages(self):
        for name, key in (("traffic_medium", "medium"), ("device", "device")):
            df = analysis.rate_table(name, key)
            for col in ("cart_rate_pct", "purchase_rate_pct", "cart_to_purchase_pct"):
                self.assertTrue(((df[col] >= 0) & (df[col] <= 100)).all(), (name, col))

    def test_data_quality_counts(self):
        q = analysis.quality_table()
        self.assertLess(q["purchase_events_without_transaction_id"], q["purchase_events"])
        self.assertGreaterEqual(q["repeated_purchase_events_with_same_id"], 0)


if __name__ == "__main__":
    unittest.main()
