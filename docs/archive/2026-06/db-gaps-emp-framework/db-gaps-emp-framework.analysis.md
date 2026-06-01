# Gap Analysis: db-gaps-emp-framework

> Date: 2026-06-01 | Design: docs/02-design/features/db-gaps-emp-framework.design.md

---

## Match Rate: 100%

Implemented items: 17  
Total design items: 17  
Formula: 17 / 17 * 100 = 100%

## Summary

The prior plan has been developed into an executable EMP framework.

The implementation now includes:

- Technical design document.
- Implementation guide.
- June 1, 2026 initial target portfolio.
- Category and risk/safe constraint validation.
- Weekly monitoring dashboard template.
- Monthly rebalance log template.
- Proposal-ready Korean framework text.
- Static dashboard generator.
- GitHub Actions dashboard deployment workflow.
- GitHub Pages deployment configuration.

The prior material gap has been closed. The framework now includes a complete 188-row enriched ETF master and a regeneration script.

## Implemented Items

- [x] Plan requirements reflected in design document.
- [x] Seven-layer architecture defined.
- [x] ETF data model defined.
- [x] Internal cluster taxonomy defined.
- [x] Cluster scoring formula defined.
- [x] ETF selection rules defined.
- [x] Initial June 1, 2026 portfolio created.
- [x] Portfolio uses only ETFs from the provided competition universe.
- [x] Portfolio totals 100%, with 70% risk assets and 30% safe assets.
- [x] All category and individual ETF constraints pass.
- [x] Weekly monitoring dashboard template created.
- [x] Monthly rebalance log template created.
- [x] Proposal-ready Korean narrative created.
- [x] Full 188-row ETF master created.
- [x] Static dashboard HTML generator created.
- [x] GitHub Actions workflow validates ETF master, builds dashboard, and deploys Pages.
- [x] GitHub Pages enabled with workflow deployment.
- [x] Deployment runbook documented.

## Check Results

| Check | Result |
|---|---|
| Python syntax check | Pass |
| ETF master build | Pass: 188 rows, 16 selected ETFs, 100% target weight |
| Dashboard build | Pass: `public/index.html` generated |
| Dashboard content smoke test | Pass: expected sections found |
| GitHub Actions latest run | Pass: `Build and Deploy Dashboard` completed successfully |
| GitHub Pages | Pass: workflow deployment enabled |
| Dashboard URL | https://2ynnso.github.io/DB-GAPs-EMP-strategy/ |

## Constraint Verification

| Check | Result |
|---|---:|
| Total portfolio weight | 100% |
| Risk assets | 70% |
| Safe assets | 30% |
| Maximum individual ETF weight | 13% |
| Domestic equity index | 10% / 30% |
| Domestic equity sector | 15% / 15% |
| Global equity index | 25% / 30% |
| Global equity sector | 10% / 10% |
| FX & commodities | 10% / 20% |
| Domestic bond aggregate | 7% / 50% |
| Domestic corporate bond | 6% / 30% |
| Global bond aggregate | 4% / 50% |
| Money market / short duration | 13% / 50% |

## Missing Items

- [ ] Live 1M/3M/6M ETF momentum values.
- [ ] Live Korea foreign/institutional flow data feed.

These are live market-data gaps, not framework implementation gaps.

## Changed Items

- [x] Overseas sector allocation was corrected from the prior draft's 18% to 10% to satisfy the stated competition category limit.
- [x] Long-duration overseas bond exposure was avoided. The implemented safe bucket uses short-duration and rate-linked instruments instead.
- [x] India and other non-US ex-Korea equity exposures were excluded in the initial allocation due to lower near-term thesis strength versus AI/semiconductor and Korea export clusters.

## Recommendations

1. Proceed with the framework package as complete.
2. Before actual trading or competition submission, update price momentum and flow values using the team's chosen data source.
3. Keep the overseas equity sector cap at 10%; do not reuse the previous 18% allocation without confirming that the competition limit differs.

## Next Steps

- [x] Framework implementation is ready for use.
- [x] Full ETF master spreadsheet created.
- [ ] Optional: convert the proposal-ready Markdown into the final `.docx` investment plan.
- [x] Dashboard GitHub Actions deployment verified.
- [ ] Recommended PDCA next action: report phase if the report should be refreshed with dashboard deployment details.
