
import pandas as pd

DEALS_FILE = "data/deals_Funnel.xlsx"
WORK_ORDERS_FILE = "data/work_Order.xlsx"


def load_data():
    deals = pd.read_excel(DEALS_FILE)

    work_orders = pd.read_excel(
        WORK_ORDERS_FILE,
        sheet_name="work order tracker",
        header=1
    )

    deals.columns = deals.columns.str.strip()
    work_orders.columns = work_orders.columns.str.strip()

    return deals, work_orders


def to_number(series):
    """Convert invalid or missing values to 0."""
    return pd.to_numeric(series, errors="coerce").fillna(0)


def get_analytics():
    deals, work_orders = load_data()

    # DEAL ANALYTICS
    total_deals = len(deals)

    open_deals = deals[
        deals["Deal Status"].astype(str).str.strip().str.lower() == "open"
    ]

    open_deal_count = len(open_deals)

    deal_values = to_number(deals["Masked Deal value"])
    open_deal_values = to_number(open_deals["Masked Deal value"])

    total_deal_value = deal_values.sum()
    open_pipeline = open_deal_values.sum()

    # Clean sector names and handle missing values
    deals["Sector/service"] = (
        deals["Sector/service"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
    )

    deals_by_sector = (
        deals.groupby("Sector/service")
        .size()
        .sort_values(ascending=False)
        .to_dict()
    )

    # WORK ORDER ANALYTICS
    total_work_orders = len(work_orders)

    execution_status = (
        work_orders["Execution Status"]
        .fillna("Missing")
        .astype(str)
        .str.strip()
        .replace("", "Missing")
        .value_counts()
        .to_dict()
    )

    billed_col = "Billed Value in Rupees (Incl of GST.) (Masked)"
    collected_col = "Collected Amount in Rupees (Incl of GST.) (Masked)"
    receivable_col = "Amount Receivable (Masked)"

    total_billed = to_number(work_orders[billed_col]).sum()
    total_collected = to_number(work_orders[collected_col]).sum()
    total_receivable = to_number(work_orders[receivable_col]).sum()

    return {
        "total_deals": total_deals,
        "open_deal_count": open_deal_count,
        "total_deal_value": total_deal_value,
        "open_pipeline": open_pipeline,
        "deals_by_sector": deals_by_sector,
        "total_work_orders": total_work_orders,
        "execution_status": execution_status,
        "total_billed": total_billed,
        "total_collected": total_collected,
        "total_receivable": total_receivable,
    }


def answer_question(question, metrics):
    q = question.lower().strip()

    if "how many deals" in q or "total deals" in q:
        return f"There are {metrics['total_deals']} deals in total."

    elif "open deal" in q or "pipeline" in q:
        return (
            f"There are {metrics['open_deal_count']} open deals. "
            f"Their total unweighted pipeline value is "
            f"₹{metrics['open_pipeline']:,.0f}."
        )

    elif "work order" in q and any(
        word in q for word in ["status", "execution", "progress", "ongoing"]
    ):
        statuses = metrics["execution_status"]
        summary = ", ".join(
            f"{status}: {count}" for status, count in statuses.items()
        )
        return f"Work order execution breakdown: {summary}."

    elif "work order" in q:
        return (
            f"There are {metrics['total_work_orders']} work orders "
            f"in the dataset."
        )

    elif "billed" in q:
        return f"Total billed value is ₹{metrics['total_billed']:,.0f}."

    elif "collect" in q:
        return (
            f"Total collected amount is "
            f"₹{metrics['total_collected']:,.0f}."
        )

    elif "receivable" in q:
        return (
            f"Total receivables are "
            f"₹{metrics['total_receivable']:,.0f}."
        )

    elif "sector" in q:
        sectors = {
            str(k): v
            for k, v in metrics["deals_by_sector"].items()
            if str(k).lower() not in ["unknown", "sector/service", "nan", ""]
        }

        if not sectors:
            return "Sector information is unavailable."

        top_sector = max(sectors, key=sectors.get)

        return (
            f"{top_sector} has the highest deal count, "
            f"with {sectors[top_sector]} deals."
        )

    else:
        return (
            "I can answer questions about deals, pipeline, sectors, "
            "work order execution, billing, collections, and receivables."
        )


if __name__ == "__main__":
    results = get_analytics()

    print("\n===== BI-AJENT ANALYTICS =====")
    for key, value in results.items():
        print(f"\n{key}: {value}")