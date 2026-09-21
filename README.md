# BI-Ajent – Business Intelligence Agent

BI-Ajent is a Flask-based business intelligence dashboard that helps founders understand their business performance using Deals and Work Orders data.

It connects to Monday.com to fetch live data and answer business questions about sales, pipeline, billing, collections, and project execution. It also supports local Excel files for development and fallback use when Monday.com is not configured.

## Features

* **Monday.com Integration:** Fetches Deals and Work Orders data using a read-only API connection.
* **Business Insights:** Shows total deal value, open pipeline, billing, collections, receivables, and work order metrics.
* **AI Agent Q&A:** Answers supported business questions using the available data.
* **Interactive Charts:** Displays deal count by sector, total deal value by sector, and work order execution status.
* **Data Cleaning:** Handles missing values, inconsistent data, and invalid numbers.
* **Cross-Board Matching:** Matches work orders with deals using normalized deal names.
* **Data Source Selection:** Uses Monday.com live data when configured; otherwise, it clearly labels and uses the local Excel snapshots.

## Tech Stack

| Technology             | Purpose                         |
| ---------------------- | ------------------------------- |
| Python                 | Main programming language       |
| Flask                  | Backend and web application     |
| Pandas                 | Data cleaning and analysis      |
| Monday.com GraphQL API | Fetching board data             |
| HTML & CSS             | Dashboard structure and styling |
| JavaScript & Chart.js  | Interactive charts              |
| Gunicorn               | Running the app on Render       |

## Project Structure

```text
bi-ajent/
├── app.py                  # Flask routes and API
├── analytics.py            # Data cleaning, metrics and Q&A
├── monday_client.py        # Monday.com API connection
├── templates/
│   └── index.html          # Dashboard UI and charts
├── data/
│   ├── deals_Funnel.xlsx   # Deals snapshot
│   └── work_Order.xlsx     # Work Orders snapshot
├── requirements.txt        # Python dependencies
├── Procfile                # Render start command
├── README.md
├── DECISION_LOG.md
└── .gitignore
```

## How It Works

1. The app checks whether the Monday.com environment variables are configured.
2. If configured, it fetches Deals and Work Orders from Monday.com. Otherwise, it uses the local Excel snapshots.
3. The data is cleaned and organized before calculating business metrics.
4. The dashboard displays KPIs and charts based on the selected data source.
5. Users can ask supported business questions, and the Agent generates answers from the available analytics.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/guptXbytes/bi-ajent.git
cd bi-ajent
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Run the application

```powershell
python app.py
```

Open the dashboard at:

http://127.0.0.1:5000

The app can use the bundled Excel snapshots when Monday.com credentials are not configured.

## Monday.com Configuration

To enable live data, set the following environment variables:

| Variable                      | Description          |
| ----------------------------- | -------------------- |
| `MONDAY_API_TOKEN`            | Monday.com API token |
| `MONDAY_DEALS_BOARD_ID`       | Deals board ID       |
| `MONDAY_WORK_ORDERS_BOARD_ID` | Work Orders board ID |

For local testing in PowerShell, set these variables in the terminal before running the app:

```powershell
$env:MONDAY_API_TOKEN="your-token"
$env:MONDAY_DEALS_BOARD_ID="your-deals-board-id"
$env:MONDAY_WORK_ORDERS_BOARD_ID="your-work-orders-board-id"
```

Use your actual values in the terminal. Never commit API tokens or other secrets to GitHub.

When all three variables are configured, the app uses Monday.com live data. If the credentials are invalid or the boards cannot be accessed, it returns a data-source error instead of silently switching to Excel data.

## API Endpoints

| Endpoint             | Description                              |
| -------------------- | ---------------------------------------- |
| `GET /`              | Loads the dashboard                      |
| `POST /`             | Submits a business question to the Agent |
| `GET /api/health`    | Checks application health                |
| `GET /api/analytics` | Returns business metrics in JSON format  |

The analytics API includes the active data source, KPIs, sector breakdowns, execution status, collection rate, and cross-board matching results.

## Data Handling & Assumptions

* The Deals workbook is `data/deals_Funnel.xlsx`, using the `Deal tracker` sheet.
* The Work Orders workbook is `data/work_Order.xlsx`, using the `work order tracker` sheet with headers on row 2.
* Numeric values may contain currency symbols, commas, blanks, or invalid text. Invalid numbers are handled safely and treated as zero.
* Missing sector or status values are grouped under labels such as `Unknown` or `Missing`.
* Work orders are matched to deals using normalized deal names. This matching is approximate and may not identify every relationship correctly.
* Open pipeline is the sum of open-deal values. It is not a probability-weighted forecast.

## Deployment on Render

The application is configured for deployment on Render using Gunicorn.

The `Procfile` contains:

```text
web: gunicorn app:app
```

To enable Monday.com live data in production:

1. Open the Render service's Environment settings.
2. Add the three Monday.com environment variables.
3. Save the values securely and redeploy the application.
4. Verify that the deployed dashboard displays Monday.com live data.

## Known Limitations

* Monday.com column names must match the supported names or aliases in the analytics code.
* Cross-board matching is based on deal names and may not always be exact.
* The Agent uses rule-based question handling and supports defined business queries. It does not answer every possible question like a general-purpose AI model.
* Pipeline values are not probability-weighted.
* Charts depend on Chart.js, which is loaded from a CDN.
* Monday.com live integration has been tested locally with the configured boards. The deployed version should be verified separately.

## Future Improvements

* Support more natural business questions.
* Improve column mapping for different Monday.com board structures.
* Use stable board item IDs for more reliable cross-board matching.
* Add more business insights and visualizations.
* Improve automated testing and error reporting.

## Author

**Sumith Gupta**

Built as a business intelligence project to explore Flask development, API integration, data analysis, and interactive dashboards.
