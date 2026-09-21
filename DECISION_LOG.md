# BI-Ajent Decision Log

## 1. Preserve the existing Flask application

The project already had working KPI cards, Chart.js charts, JSON endpoints, and a server-rendered question flow. The implementation keeps those paths and improves their failure behavior instead of introducing a new framework or frontend build step.

## 2. Separate source loading from analytics

Analytics now selects a live Monday.com source only when all required environment variables exist; otherwise it uses the existing Excel snapshots. The calculation layer receives dataframes and resolves columns through aliases, which keeps Flask routes focused on HTTP behavior.

**Trade-off:** Alias matching makes the app tolerant of small board naming differences, but an unusual Monday column title may need an explicit alias. This is preferable to silently calculating from the wrong column.

## 3. Read-only Monday integration

The Monday client uses GraphQL `boards -> items_page` reads only. It does not expose mutation methods. Tokens and board IDs are read from environment variables and never committed.

**Trade-off:** Live mode fails clearly when configuration or access is invalid rather than falling back to stale snapshots. This protects founder-facing decisions from an unnoticed source switch.

## 4. Defensive handling of imperfect data

Missing columns become unavailable/zero-valued metrics, null labels become `Unknown` or `Missing`, and currency-like strings are parsed defensively. Collection rate is `N/A` when billed value is absent or zero.

**Trade-off:** Treating malformed amounts as zero avoids route failures but can hide data quality problems. The API and UI should be extended with row-level quality warnings if operational monitoring becomes a requirement.

## 5. Grounded deterministic Q&A

Answers are generated only from calculated metrics. The assistant reports when a requested field is unavailable and describes pipeline as an unweighted open-deal sum.

**Trade-off:** Keyword routing is less flexible than an LLM, but it is transparent, reproducible, and cannot fabricate a value. A future semantic layer should retain the same metric and evidence constraints.

## 6. Cross-board matching

The dashboard reports deal/work-order name matches after whitespace and case normalization.

**Trade-off:** Name matching provides useful insight with the current masked data but is not a guaranteed relational key. A stable Monday item ID or explicit deal ID column should replace it when available.

## 7. Deployment posture

The existing Render `Procfile` remains `web: gunicorn app:app`. The repository does not push or deploy automatically. Real Monday credentials and board IDs must be supplied through Render secrets before live integration can be tested.
