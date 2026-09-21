"""Read-only Monday.com board access for BI-Ajent.

"""

import os
from typing import Any

import pandas as pd
import requests


MONDAY_API_URL = "https://api.monday.com/v2"


class MondayConfigurationError(RuntimeError):
    """Raised when live Monday configuration is incomplete."""


class MondayAPIError(RuntimeError):
    """Raised when Monday rejects or cannot complete a read request."""


def monday_is_configured() -> bool:
    return bool(
        os.getenv("MONDAY_API_TOKEN")
        and os.getenv("MONDAY_DEALS_BOARD_ID")
        and os.getenv("MONDAY_WORK_ORDERS_BOARD_ID")
    )


def _configured_value(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise MondayConfigurationError(f"Missing required environment variable: {name}")
    return value


def _query_board(board_id: str) -> list[dict[str, Any]]:
    query = """
    query ($board_id: ID!, $cursor: String) {
      boards(ids: [$board_id]) {
        items_page(limit: 500, cursor: $cursor) {
          cursor
          items {
            name
            column_values { id text value column { title } }
          }
        }
      }
    }
    """
    token = _configured_value("MONDAY_API_TOKEN")
    headers = {"Authorization": token, "Content-Type": "application/json"}
    rows: list[dict[str, Any]] = []
    cursor = None

    while True:
        try:
            response = requests.post(
                MONDAY_API_URL,
                json={"query": query, "variables": {"board_id": board_id, "cursor": cursor}},
                headers=headers,
                timeout=20,
            )
        except requests.RequestException as error:
            raise MondayAPIError(f"Could not reach Monday: {error}") from error
        if response.status_code != 200:
            raise MondayAPIError(f"Monday returned HTTP {response.status_code}")

        try:
            payload = response.json()
        except ValueError as error:
            raise MondayAPIError("Monday returned invalid JSON") from error

        if payload.get("errors"):
            messages = "; ".join(str(item.get("message", "Unknown error")) for item in payload["errors"])
            raise MondayAPIError(messages or "Monday returned a GraphQL error")

        boards = payload.get("data", {}).get("boards", [])
        if not boards:
            raise MondayAPIError(f"Monday board {board_id} was not found or is inaccessible")

        page = boards[0].get("items_page", {})
        for item in page.get("items", []):
            row = {"Item name": item.get("name")}
            for column in item.get("column_values", []):
                title = (column.get("column") or {}).get("title") or column.get("id")
                if title:
                    row[title] = column.get("text") or column.get("value")
            rows.append(row)

        cursor = page.get("cursor")
        if not cursor:
            return rows


def fetch_monday_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fetch both configured boards without performing any Monday mutations."""
    if not monday_is_configured():
        raise MondayConfigurationError(
            "Set MONDAY_API_TOKEN, MONDAY_DEALS_BOARD_ID, and "
            "MONDAY_WORK_ORDERS_BOARD_ID to enable live data."
        )

    deals = pd.DataFrame(_query_board(_configured_value("MONDAY_DEALS_BOARD_ID")))
    work_orders = pd.DataFrame(_query_board(_configured_value("MONDAY_WORK_ORDERS_BOARD_ID")))
    return deals, work_orders
