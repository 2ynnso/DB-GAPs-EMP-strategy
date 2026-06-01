# Gap Analysis: db-gaps-emp-framework

> Date: 2026-06-01 | Design: docs/02-design/features/db-gaps-emp-framework.design.md

---

## Match Rate: 92%

Implemented items: 12  
Total design items: 13  
Formula: 12 / 13 * 100 = 92.3%

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

The only material gap is that the ETF master is represented through the selected portfolio and cluster rules, not yet as a complete 188-row enriched ETF master with cluster labels for every ETF in the universe. This does not block the strategy framework, but it would improve repeatability if the team wants full automation.

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

- [ ] Full 188-row enriched ETF master with cluster and same-exposure labels for every ETF.
- [ ] Live 1M/3M/6M ETF momentum values.
- [ ] Live Korea foreign/institutional flow data feed.

These are operational data gaps, not strategy-design gaps.

## Changed Items

- [x] Overseas sector allocation was corrected from the prior draft's 18% to 10% to satisfy the stated competition category limit.
- [x] Long-duration overseas bond exposure was avoided. The implemented safe bucket uses short-duration and rate-linked instruments instead.
- [x] India and other non-US ex-Korea equity exposures were excluded in the initial allocation due to lower near-term thesis strength versus AI/semiconductor and Korea export clusters.

## Recommendations

1. Proceed to report if the immediate objective is a completed framework package.
2. If the team wants full monitoring automation, build the enriched 188-row ETF master next.
3. Before actual trading or competition submission, update price momentum and flow values using the team's chosen data source.
4. Keep the overseas equity sector cap at 10%; do not reuse the previous 18% allocation without confirming that the competition limit differs.

## Next Steps

- [x] Framework implementation is ready for use.
- [ ] Optional: create a full ETF master spreadsheet.
- [ ] Optional: convert the proposal-ready Markdown into the final `.docx` investment plan.
- [ ] Recommended PDCA next action: report phase.
