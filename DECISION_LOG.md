# BI-Ajent – Decision Log

This document explains the key decisions I made while building BI-Ajent, along with the reasons, trade-offs, and possible improvements.

## 1. Keep the Existing Flask Application

I decided to continue with the existing Flask application because it already had working KPI cards, charts, API endpoints, and a question-answering flow.

Instead of rebuilding everything using a new framework, I improved the existing features and error handling. This helped keep the project simple and focused.

## 2. Separate Data Loading from Analytics

I kept data loading and business calculations separate from the Flask routes. The app uses Monday.com when all required environment variables are configured; otherwise, it uses the local Excel snapshots.

This makes the code easier to understand, test, and maintain.

**Trade-off:** Column aliases help handle small differences in column names, but unusual names may still need to be added manually.

## 3. Use a Read-Only Monday.com Integration

I chose a read-only Monday.com API connection so the Agent can fetch Deals and Work Orders data without changing the original boards.

The API token and board IDs are stored in environment variables instead of being hardcoded in the project.

**Trade-off:** If Monday.com credentials are invalid or the boards are inaccessible, the app reports an error instead of silently using old Excel data. This helps avoid misleading business insights.

## 4. Handle Messy Data Safely

The provided data may contain missing values, inconsistent text, or invalid numbers. I added data-cleaning logic to handle these cases and prevent common calculation errors.

Missing labels are grouped under `Unknown` or `Missing`, and invalid numeric values are handled safely.

**Trade-off:** Treating invalid amounts as zero keeps calculations running, but it may hide data quality issues. In the future, I would add data-quality warnings to highlight records that need review.

## 5. Use Rule-Based Q&A for Business Questions

I chose rule-based question handling so the Agent answers using calculated business metrics rather than making unsupported assumptions.

This approach keeps the answers simple, consistent, and easier to verify.

**Trade-off:** It may not understand every way a founder asks a question. A future version could support more natural questions while ensuring answers remain connected to actual data.

## 6. Match Deals and Work Orders Using Deal Names

I used normalized deal names to match Deals with Work Orders. The matching process handles basic differences such as letter case and extra spaces.

**Trade-off:** Deal names are not always unique, so this matching is not guaranteed to be exact. If a stable deal ID is available, I would use it for more reliable matching.

## 7. Keep Deployment Simple

I kept the existing Render deployment setup using Gunicorn, without adding an unnecessary deployment framework or extra build steps.

Monday.com credentials are configured through Render environment variables, keeping them separate from the source code.

**Trade-off:** The live Monday.com integration must be configured and tested separately in Render. A successful local test alone does not confirm that the deployed app is working correctly.
