import unittest
from unittest.mock import patch

from app import app


class QuestionRefreshTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.metrics = {
            "source": {"label": "Test data"},
            "total_deals": 1,
            "open_deal_count": 1,
            "open_pipeline": 100,
            "total_work_orders": 1,
            "total_billed": 100,
            "total_collected": 50,
            "total_receivable": 50,
            "collection_rate": 50,
            "deals_by_sector": {"Mining": 1},
            "deal_value_by_sector": {"Mining": 100},
            "execution_status": {"Completed": 1},
        }

    def test_post_shows_answer_but_fresh_get_is_empty(self):
        with patch("app.get_analytics", return_value=self.metrics):
            post_response = self.client.post(
                "/", data={"question": "How many deals?"}
            )
            get_response = self.client.get("/")

        self.assertIn(b"How many deals?", post_response.data)
        self.assertIn(b"There are 1 deals in total.", post_response.data)
        self.assertNotIn(b"How many deals?", get_response.data)
        self.assertNotIn(b"Agent Response", get_response.data)

    def test_answer_page_clears_history_entry_for_refresh(self):
        with patch("app.get_analytics", return_value=self.metrics):
            response = self.client.post("/", data={"question": "How many deals?"})

        self.assertIn(b"window.history.replaceState", response.data)
        self.assertNotIn(b"localStorage", response.data)
        self.assertNotIn(b"sessionStorage", response.data)


if __name__ == "__main__":
    unittest.main()