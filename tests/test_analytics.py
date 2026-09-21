import unittest
from unittest.mock import patch

import pandas as pd

import analytics


class AnalyticsQuestionTests(unittest.TestCase):
    def setUp(self):
        self.deals = pd.DataFrame(
            {
                "Deal Name": ["Deal A", "Deal B", "Deal C", "Deal D"],
                "Deal Status": ["Open", "Closed", "Open", "Open"],
                "Masked Deal value": ["₹100,000", "200000", None, "not-a-number"],
                "Sector/service": ["Mining", "Powerline", None, "Mining"],
            }
        )
        self.work_orders = pd.DataFrame(
            {
                "Deal name masked": ["Deal A"],
                "Execution Status": ["Completed"],
                "Billed Value": ["1000"],
                "Collected Amount": ["500"],
                "Amount Receivable": ["500"],
                "Sector": ["Mining"],
            }
        )

    def test_sector_value_question_variations(self):
        with patch.object(
            analytics,
            "load_data",
            return_value=(self.deals, self.work_orders, {"mode": "snapshot", "label": "test"}),
        ):
            metrics = analytics.get_analytics()

        expected = "Top sectors by total deal value are Powerline: ₹200,000, Mining: ₹100,000."
        for question in (
            "Which sectors have the largest deals?",
            "Which sectors have the largest deal values?",
            "Show me deal value by sector.",
        ):
            self.assertEqual(analytics.answer_question(question, metrics), expected)

    def test_monday_mode_uses_fetched_board_data(self):
        with patch.object(analytics, "monday_is_configured", return_value=True), patch.object(
            analytics,
            "fetch_monday_data",
            return_value=(self.deals, self.work_orders),
        ):
            metrics = analytics.get_analytics()

        self.assertEqual(metrics["source"]["mode"], "monday")
        self.assertEqual(metrics["total_deals"], 4)
        self.assertEqual(metrics["deal_value_by_sector"]["Powerline"], 200000.0)

    def test_value_chart_mapping_and_agent_ranking_share_aggregation(self):
        with patch.object(
            analytics,
            "load_data",
            return_value=(self.deals, self.work_orders, {"mode": "snapshot", "label": "test"}),
        ):
            metrics = analytics.get_analytics()

        self.assertEqual(sum(metrics["deal_value_by_sector"].values()), metrics["total_deal_value"])
        top_sector = max(metrics["deal_value_by_sector"], key=metrics["deal_value_by_sector"].get)
        answer = analytics.answer_question("Which sectors have the largest deal values?", metrics)
        self.assertTrue(answer.startswith(f"Top sectors by total deal value are {top_sector}:"))


if __name__ == "__main__":
    unittest.main()
