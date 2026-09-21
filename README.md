# BI-Ajent

BI-Ajent is a Flask business intelligence dashboard for founder-level questions across Deals and Work Orders. It currently supports the bundled Excel snapshots and an optional read-only Monday.com source.

## Architecture

- `app.py`: Flask routes, form validation, and JSON error responses.
- `analytics.py`: source selection, schema-tolerant normalization, KPI calculations, cross-board matching, and grounded rule-based Q&A.
- `monday_client.py`: read-only Monday GraphQL client. It never creates, updates, or deletes board data.
- `templates/index.html`: responsive dashboard, KPI cards, separate deal-count and deal-value-by-sector Chart.js charts, work-order status chart, and server-rendered Q&A.
- `data/`: local Excel snapshots used when Monday credentials are not configured.

The source is selected at request time. With all required Monday variables present, live Monday data is used. Otherwise the app uses the local snapshot and labels it clearly in the UI and API response.

## Local setup

PowerShell:

```powershell
cd C:\Users\Sumith\Desktop\bi-ajent
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

For a production-like local run:

```powershell
gunicorn app:app
```

On Windows, use `python app.py` for local development because Gunicorn is intended for Linux-based deployment environments such as Render.

## Environment variables

Optional live integration requires all three values:

- `MONDAY_API_TOKEN`: Monday.com API token stored as a secret.
- `MONDAY_DEALS_BOARD_ID`: read-only Deals board ID.
- `MONDAY_WORK_ORDERS_BOARD_ID`: read-only Work Orders board ID.

No token or board ID is stored in this repository. If these values are absent, the app intentionally uses the Excel snapshot. If they are present but invalid or inaccessible, the app reports a data-source error rather than silently showing stale data.

## API endpoints

- `GET /api/health`: returns service health.
- `GET /api/analytics`: returns structured analytics JSON, including `source`, KPI values, sector distributions, execution statuses, collection rate, and cross-board matching counts.
- `GET /`: renders the dashboard.
- `POST /`: answers a question from the current analytics result using the `question` form field.

Successful analytics responses have `status: "success"` and a `data` object. Data-source failures return HTTP `503` with `status: "error"` and an error code/message.

## Data assumptions

- The local Deals workbook is `data/deals_Funnel.xlsx`, sheet `Deal tracker`.
- The local Work Orders workbook is `data/work_Order.xlsx`, sheet `work order tracker`, with the header on row 2.
- Numeric values may contain currency symbols, commas, blanks, or malformed text; invalid values are treated as zero.
- Missing text fields are represented as `Unknown` or `Missing` and are not presented as known business facts.
- Cross-board matching uses normalized deal names. It is a useful diagnostic, not a definitive foreign-key relationship.
- Pipeline is an unweighted sum of open-deal values. It is not a probability-weighted forecast.

## Deployment on Render

Use the existing `Procfile` command:

```text
web: gunicorn app:app
```

Set the three `MONDAY_*` variables in Render Environment Variables only after receiving the real read-only token and board IDs. Add them as secrets and redeploy. Do not commit `.env` or tokens.

## Known limitations

- Monday column titles must contain recognizable names for the analytics resolver to map them. Board-specific custom naming may require adding an alias in `analytics.py`.
- Q&A is deterministic and intentionally does not invent forecasts or unsupported conclusions.
- Chart.js is loaded from a CDN; the dashboard displays a clear unavailable state if it cannot load.
- No Monday integration is claimed as tested until it is run against the real token and both real boards.
