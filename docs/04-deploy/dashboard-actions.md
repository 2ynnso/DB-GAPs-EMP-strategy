# Dashboard Deployment with GitHub Actions

> Date: 2026-06-01  
> Workflow: `.github/workflows/dashboard.yml`

## Purpose

The dashboard is generated from repository CSV files and deployed as a static GitHub Pages site.

The workflow is intentionally dependency-light:

- Python standard library only.
- No package install step.
- No API keys or secrets.
- No external data fetch.

## Build Flow

1. Checkout repository.
2. Set up Python 3.12.
3. Regenerate `framework/etf-master.csv`.
4. Validate row counts and target weights.
5. Generate `public/index.html`.
6. Upload the `public/` folder as a Pages artifact.
7. Deploy to GitHub Pages.

## Trigger

The workflow runs on:

- Push to `main` when `framework/**`, `scripts/**`, the workflow file, or `README.md` changes.
- Manual `workflow_dispatch`.

## Required GitHub Setting

In the GitHub repository:

1. Go to `Settings`.
2. Open `Pages`.
3. Under `Build and deployment`, set `Source` to `GitHub Actions`.

After that, pushes to `main` will deploy the dashboard.

## Files

| File | Role |
|---|---|
| `.github/workflows/dashboard.yml` | CI/CD workflow |
| `scripts/build-dashboard.py` | Static dashboard generator |
| `scripts/build-etf-master.py` | ETF master generator |
| `public/index.html` | Generated local preview artifact |
| `framework/initial-portfolio.csv` | Initial allocation source |
| `framework/etf-master.csv` | Enriched ETF universe |
| `framework/weekly-monitoring-dashboard.csv` | Weekly monitoring source |
| `framework/monthly-rebalance-log.csv` | Rebalance log source |

## Local Preview

Run:

```bash
python3 scripts/build-etf-master.py
python3 scripts/build-dashboard.py
```

Then open:

```text
public/index.html
```

## Validation Rules

The workflow fails if:

- `framework/etf-master.csv` does not have 188 ETF rows.
- Selected ETF count is not 16.
- Selected ETF target weight does not total 100%.
- Dashboard generation fails.

## Operational Note

The dashboard displays repository data. It does not fetch live prices, flows, or macro data. Weekly momentum and flow fields should be updated in the CSV files before pushing if the team wants the dashboard to reflect current operating signals.
