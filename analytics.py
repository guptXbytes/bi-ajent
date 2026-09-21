
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from monday_client import (
    MondayAPIError,
    MondayConfigurationError,
    fetch_monday_data,
    monday_is_configured,
)


BASE_DIR = Path(__file__).resolve().parent
DEALS_FILE = BASE_DIR / "data" / "deals_Funnel.xlsx"
WORK_ORDERS_FILE = BASE_DIR / "data" / "work_Order.xlsx"


class DataLoadError(RuntimeError):
    """Raised when the configured data source cannot be loaded safely."""


def _clean_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def _read_snapshot() -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        deals = pd.read_excel(DEALS_FILE)
        work_orders = pd.read_excel(
            WORK_ORDERS_FILE,
            sheet_name="work order tracker",
            header=1,
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        raise DataLoadError(f"Could not read local Excel snapshots: {error}") from error
    return _clean_columns(deals), _clean_columns(work_orders)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    """Load Monday data when configured, otherwise use local snapshots."""
    if monday_is_configured():
        try:
            deals, work_orders = fetch_monday_data()
            return (
                _clean_columns(deals),
                _clean_columns(work_orders),
                {"mode": "monday", "label": "Monday.com live data"},
            )
        except (MondayAPIError, MondayConfigurationError) as error:
            raise DataLoadError(f"Monday.com data source failed: {error}") from error

    deals, work_orders = _read_snapshot()
    return deals, work_orders, {"mode": "snapshot", "label": "Local Excel snapshot"}


def _column(frame: pd.DataFrame, names: list[str]) -> str | None:
    normalized = {str(column).strip().casefold(): column for column in frame.columns}
    for name in names:
        if name.casefold() in normalized:
            return normalized[name.casefold()]
    for column in frame.columns:
        if any(name.casefold() in str(column).casefold() for name in names):
            return column
    return None


def _text(frame: pd.DataFrame, names: list[str], default: str) -> pd.Series:
    column = _column(frame, names)
    if column is None:
        return pd.Series(default, index=frame.index, dtype="string")
    return (
        frame[column]
        .fillna(default)
        .astype("string")
        .str.strip()
        .replace("", default)
        .fillna(default)
    )


def to_number(series):
    """Convert currency-like, invalid, or missing values to zero."""
    cleaned = series.astype("string").str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)


def _amount(frame: pd.DataFrame, names: list[str]) -> pd.Series:
    column = _column(frame, names)
    if column is None:
        return pd.Series(0.0, index=frame.index)
    return to_number(frame[column])


def _safe_rate(numerator: float, denominator: float) -> float | None:
    return round(numerator / denominator * 100, 2) if denominator else None


def _deal_key(value: Any) -> str:
    return " ".join(str(value).casefold().split()) if pd.notna(value) else ""


def get_analytics():
    deals, work_orders, source = load_data()
    deal_status = _text(deals, ["Deal Status", "Status"], "Missing").str.casefold()
    open_deals = deal_status.isin({"open", "active", "in progress"})
    deal_values = _amount(deals, ["Masked Deal value", "Deal value", "Value"])
    sectors = _text(deals, ["Sector/service", "Sector", "Industry"], "Unknown")
    execution_status = _text(
        work_orders, ["Execution Status", "Execution status", "Status"], "Missing"
    )
    billed = _amount(
        work_orders,
        ["Billed Value in Rupees (Incl of GST.) (Masked)", "Billed Value", "Billed"],
    )
    collected = _amount(
        work_orders,
        ["Collected Amount in Rupees (Incl of GST.) (Masked)", "Collected Amount", "Collected"],
    )
    receivable = _amount(
        work_orders, ["Amount Receivable (Masked)", "Amount Receivable", "Receivable"]
    )

    deals_by_sector = sectors.value_counts().to_dict()
    deal_value_by_sector = (
        deal_values.groupby(sectors).sum().sort_values(ascending=False).to_dict()
    )
    open_pipeline_by_sector = (
        deal_values[open_deals]
        .groupby(sectors[open_deals])
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )
    work_order_sectors = _text(
        work_orders, ["Sector", "Sector/service", "Industry"], "Unknown"
    )
    deal_names = _text(deals, ["Deal Name", "Item name", "Name"], "").map(_deal_key)
    work_order_names = _text(
        work_orders, ["Deal name masked", "Deal Name", "Item name", "Name"], ""
    ).map(_deal_key)
    known_deals = {name for name in deal_names if name}
    matched_work_orders = sum(
        bool(name) and name in known_deals for name in work_order_names
    )
    total_billed = float(billed.sum())
    total_collected = float(collected.sum())

    return {
        "source": source,
        "total_deals": int(len(deals)),
        "open_deal_count": int(open_deals.sum()),
        "total_deal_value": float(deal_values.sum()),
        "open_pipeline": float(deal_values[open_deals].sum()),
        "deals_by_sector": {str(key): int(value) for key, value in deals_by_sector.items()},
        "deal_value_by_sector": {
            str(key): float(value) for key, value in deal_value_by_sector.items()
        },
        "open_pipeline_by_sector": {
            str(key): float(value) for key, value in open_pipeline_by_sector.items()
        },
        "total_work_orders": int(len(work_orders)),
        "execution_status": {
            str(key): int(value) for key, value in execution_status.value_counts().items()
        },
        "work_orders_by_sector": {
            str(key): int(value) for key, value in work_order_sectors.value_counts().items()
        },
        "total_billed": total_billed,
        "total_collected": total_collected,
        "total_receivable": float(receivable.sum()),
        "collection_rate": _safe_rate(total_collected, total_billed),
        "cross_board": {
            "matched_work_orders": int(matched_work_orders),
            "unmatched_work_orders": int(len(work_orders) - matched_work_orders),
        },
    }


def _money(value: float) -> str:
    return f"₹{value:,.0f}"


def _unavailable(label: str) -> str:
    return f"{label} is unavailable because the loaded data does not contain that field."


def answer_question(question: str, metrics: dict[str, Any]) -> str:
    """Answer only from supplied metrics; do not infer unsupported facts."""
    query = " ".join(str(question).casefold().split())
    if not query:
        return "Please enter a question."

    if (
        "how many" in query
        and "deal" in query
        and "open" not in query
        and "work order" not in query
        and "match" not in query
    ):
        return f"There are {metrics['total_deals']:,} deals in total."
    if "sector" in query and (
        "largest" in query or "deal value" in query or "value by sector" in query
    ):
        values = {
            key: value
            for key, value in metrics.get("deal_value_by_sector", {}).items()
            if key.casefold() not in {"unknown", "missing", "sector/service"}
        }
        if not values:
            return _unavailable("Sector deal value analysis")
        top_sectors = sorted(values.items(), key=lambda item: item[1], reverse=True)[:3]
        summary = ", ".join(f"{sector}: {_money(value)}" for sector, value in top_sectors)
        return f"Top sectors by total deal value are {summary}."
    if "sector" in query and any(word in query for word in ("pipeline", "revenue")):
        values = {
            key: value
            for key, value in metrics["open_pipeline_by_sector"].items()
            if key.casefold() not in {"unknown", "missing", "sector/service"}
        }
        if not values:
            return _unavailable("Sector pipeline analysis")
        sector = max(values, key=values.get)
        return f"{sector} has the largest open pipeline at {_money(values[sector])}."
    if ("open" in query and "deal" in query) or ("pipeline" in query and "sector" not in query):
        return (
            f"There are {metrics['open_deal_count']:,} open deals with an "
            f"unweighted pipeline of {_money(metrics['open_pipeline'])}."
        )
    if "highest" in query and "sector" in query:
        sectors = {
            key: value
            for key, value in metrics["deals_by_sector"].items()
            if key.casefold() not in {"unknown", "missing", "sector/service"}
        }
        if not sectors:
            return _unavailable("Sector analysis")
        sector = max(sectors, key=sectors.get)
        return f"{sector} has the highest deal count with {sectors[sector]:,} deals."
    if "work order" in query and any(word in query for word in ("match", "cross", "deal")):
        matched = metrics["cross_board"]
        return (
            f"{matched['matched_work_orders']:,} of {metrics['total_work_orders']:,} work orders "
            f"match a deal name; {matched['unmatched_work_orders']:,} do not."
        )
    if "work order" in query and any(
        word in query for word in ("status", "execution", "progress", "ongoing")
    ):
        breakdown = ", ".join(
            f"{key}: {value:,}" for key, value in metrics["execution_status"].items()
        )
        return f"Work order execution breakdown: {breakdown}."
    if "work order" in query:
        return f"There are {metrics['total_work_orders']:,} work orders in the loaded data."
    if "collection rate" in query or ("collect" in query and "rate" in query):
        rate = metrics["collection_rate"]
        if rate is None:
            return "Collection rate is unavailable because billed value is missing or zero."
        return f"The collection rate is {rate:.2f}% of billed value."
    if "billed" in query:
        return f"Total billed value is {_money(metrics['total_billed'])}."
    if "collect" in query:
        return f"Total collected amount is {_money(metrics['total_collected'])}."
    if "receivable" in query or "outstanding" in query:
        return f"Total receivables are {_money(metrics['total_receivable'])}."
    if any(word in query for word in ("source", "fresh", "live")):
        return f"This dashboard is using {metrics['source']['label']}."
    return (
        "I can answer questions about deals, open pipeline, sectors, work order "
        "execution, cross-board matches, billing, collections, and receivables."
    )


if __name__ == "__main__":
    print(get_analytics())