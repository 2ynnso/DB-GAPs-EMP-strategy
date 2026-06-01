# DB GAPS EMP Strategy

ETF Managed Portfolio framework for the DB GAPS ETF investment competition.

The strategy is designed for the June-August 2026 competition window and focuses on absolute cumulative return. The Base Case portfolio uses the full 70% risk-asset allowance and keeps 30% in short-duration or rate-linked safe assets.

## Core Idea

The framework combines:

- Macro regime assessment.
- Concentrated ETF cluster rotation.
- Competition constraint checks.
- Weekly monitoring.
- Monthly rebalancing.
- Scenario-based risk control.

The current Base Case is **reflation with geopolitical risk premium**. The main return engines are AI semiconductors, US growth exposure, Korean export/cyclical alpha, and AI power infrastructure. Gold, WTI oil, CD/KOFR, short domestic bonds, high-grade credit, and USD short bonds are used as buffers or hedges.

## Initial Allocation

As of 2026-06-01:

| Bucket | Weight |
|---|---:|
| Risk assets | 70% |
| Safe assets | 30% |
| Total | 100% |

Largest single ETF weight: 13%.

All stated category limits are satisfied:

- Domestic equity index: 10% / 30%
- Domestic equity sector: 15% / 15%
- Global equity index: 25% / 30%
- Global equity sector: 10% / 10%
- FX and commodities: 10% / 20%
- Money market / short duration: 13% / 50%

## Repository Structure

```text
.
├── docs/
│   ├── 01-plan/features/
│   ├── 02-design/features/
│   ├── 03-analysis/
│   └── 04-report/
├── framework/
│   ├── initial-portfolio.csv
│   ├── monthly-rebalance-log.csv
│   ├── proposal-ready-framework.md
│   └── weekly-monitoring-dashboard.csv
├── 투자계획서/
└── 제12회_GAPS_ETF_리스트_(v260509).xlsx_-_ETF.csv
```

## Key Files

| File | Purpose |
|---|---|
| `framework/initial-portfolio.csv` | June 1, 2026 target ETF portfolio |
| `framework/weekly-monitoring-dashboard.csv` | Weekly signal and decision template |
| `framework/monthly-rebalance-log.csv` | Monthly turnover and rebalance log |
| `framework/proposal-ready-framework.md` | Korean proposal-ready strategy text |
| `docs/02-design/features/db-gaps-emp-framework.design.md` | Full framework design |
| `docs/03-analysis/db-gaps-emp-framework.analysis.md` | Gap analysis and match rate |
| `docs/04-report/db-gaps-emp-framework.report.md` | Completion report |

## Operating Rules

Weekly:

1. Update 1M/3M/6M ETF momentum.
2. Check 20D/60D trend and drawdown from 60D high.
3. Update macro signals: Fed, BOK, CPI, oil, USD/KRW, Korea exports.
4. Update Korea foreign/institutional flow where available.
5. Score clusters and classify each as Add, Hold, Watch, or Cut.

Monthly:

1. Reclassify macro regime.
2. Recompute cluster ranking.
3. Propose trades.
4. Verify category limits.
5. Verify monthly turnover of at least 10%.
6. Record decisions in `framework/monthly-rebalance-log.csv`.

## Status

PDCA status: complete.

Design-to-implementation match rate: 92%.

Remaining optional work:

- Build a full 188-row enriched ETF master.
- Add live momentum data.
- Add live Korea foreign/institutional flow data.
- Convert the proposal-ready Markdown into a final `.docx`.
