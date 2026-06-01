# Dashboard Deployment with GitHub Actions

> Date: 2026-06-01  
> Workflow: `.github/workflows/dashboard.yml`

## Purpose

The dashboard is generated from repository CSV files and deployed as a static GitHub Pages site.

The workflow is intentionally dependency-light:

- Python standard library only.
- No package install step.
- No API keys or secrets.
- Price data is fetched through Yahoo Finance's public chart endpoint.

## Build Flow

1. Checkout repository.
2. Set up Python 3.12.
3. Regenerate `framework/etf-master.csv`.
4. Fetch ETF prices and update `framework/weekly-monitoring-dashboard.csv`.
5. Validate row counts, target weights, and momentum fields.
6. Generate `public/index.html`.
7. Commit updated monitoring CSV on scheduled/manual runs.
8. Upload the `public/` folder as a Pages artifact.
9. Deploy to GitHub Pages.

## Trigger

The workflow runs on:

- Push to `main` when `framework/**`, `scripts/**`, the workflow file, or `README.md` changes.
- Scheduled weekdays at 17:30 KST.
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
| `scripts/update-momentum.py` | Price API fetch and momentum calculator |
| `public/index.html` | Generated local preview artifact |
| `public/momentum.html` | Generated equity momentum dashboard |
| `framework/initial-portfolio.csv` | Initial allocation source |
| `framework/etf-master.csv` | Enriched ETF universe |
| `framework/equity-momentum.csv` | Equity ETF momentum ranking |
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

## Momentum Update

The dashboard fetches selected ETF prices automatically through `scripts/update-momentum.py`.

Calculated fields:

- 1M, 3M, and 6M returns.
- 20D and 60D moving-average trend checks.
- Drawdown from 60D high.
- Relative rank by 3M return.
- Cluster score.
- Add/Hold/Watch/Cut decision.

Flow and macro fields remain manual checks because they require non-price data.

## Equity Momentum Dashboard

`public/momentum.html` is a focused page for stock ETF momentum only.

It includes:

- Buy/expand candidates.
- Sell/reduce candidates.
- Strongest and weakest momentum names.
- Full ranking of invested equity ETFs.

The page intentionally excludes bonds, money-market ETFs, and commodity hedges so that the team can quickly see which stock exposures deserve more capital and which should be reduced.
