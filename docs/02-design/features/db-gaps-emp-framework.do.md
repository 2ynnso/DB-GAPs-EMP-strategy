# db-gaps-emp-framework - Implementation Guide

> Version: 1.0.0 | Date: 2026-06-01 | Status: Draft  
> Design: docs/02-design/features/db-gaps-emp-framework.design.md

---

## 1. Objective

This guide turns the design document into practical work items for the team.

The current implementation target is a usable investment framework, not a software product. The minimum complete output is:

- ETF master table.
- Cluster mapping.
- Initial June 1, 2026 target portfolio.
- Constraint checker.
- Weekly monitoring dashboard.
- Monthly rebalance log.
- Proposal-ready strategy narrative.

## 2. Deliverables

| Deliverable | Path or format | Status |
|---|---|---|
| Plan document | docs/01-plan/features/db-gaps-emp-framework.plan.md | Complete |
| Design document | docs/02-design/features/db-gaps-emp-framework.design.md | Complete |
| Implementation guide | docs/02-design/features/db-gaps-emp-framework.do.md | Complete |
| Initial portfolio CSV | framework/initial-portfolio.csv | Complete |
| Monitoring dashboard | framework/weekly-monitoring-dashboard.csv | Complete |
| Monthly rebalance log | framework/monthly-rebalance-log.csv | Complete |
| Proposal-ready framework text | framework/proposal-ready-framework.md | Complete |

## 3. ETF Master Build

Required columns:

| Column | Source |
|---|---|
| ticker | ETF universe CSV |
| name | ETF universe CSV |
| aum_krw_100m | ETF universe CSV |
| index_name | ETF universe CSV |
| risk_label | ETF universe CSV |
| competition_category | ETF universe CSV |
| cluster | Manual mapping |
| same_exposure_group | Manual mapping |
| selected_role | Manual mapping |
| target_weight | Portfolio table |

Cluster mapping rules:

| ETF keyword | Cluster |
|---|---|
| AI반도체, 반도체, 필라델피아AI반도체, 미국반도체 | AI & Semiconductors |
| AI전력, 전력핵심, 원자력 | AI Power Infrastructure |
| 조선, 방산, 우주 | Korea Cyclical Alpha |
| S&P500, 나스닥100, KODEX 200 | Core Equity Beta |
| 금, WTI, 원유 | Commodity Hedge |
| CD금리, KOFR, 머니마켓, 단기 | Short-Duration Safety |
| 종합채권, 회사채, 국고채 | Domestic Carry |
| 미국달러단기채권 | USD Safety |

## 4. Initial Portfolio Entry

Enter the June 1 target weights exactly as defined in the design document.

Risk asset total:

```text
10 + 8 + 4 + 3 + 13 + 12 + 6 + 4 + 6 + 4 = 70
```

Safe asset total:

```text
8 + 5 + 4 + 3 + 6 + 4 = 30
```

Total portfolio:

```text
70 + 30 = 100
```

## 5. Constraint Checker

At minimum, the dashboard must calculate:

| Check | Formula |
|---|---|
| Individual ETF limit | max(target_weight) <= 20 |
| Risk asset limit | sum(weight where risk_label = 위험) <= 70 |
| Safe asset target | sum(weight where risk_label = 안전) ~= 30 |
| Category limit | sum(weight by competition_category) <= category_limit |
| Monthly turnover | sum(abs(new_weight - old_weight)) / 2 >= 10 |
| Initial turnover | sum(abs(initial_weight - pre_trade_weight)) / 2 >= 80 |

Category limits:

| Category | Limit |
|---|---:|
| 국내주식_지수 | 30% |
| 국내주식_섹터 | 15% |
| 해외주식_지수 | 30% |
| 해외주식_섹터 | 10% |
| FX 및 원자재 | 20% |
| 국내채권_종합 | 50% |
| 국내채권_회사채 | 30% |
| 해외채권_종합 | 50% |
| 해외채권_회사채 | 30% |
| 금리연계형/초단기채권 | 50% |

## 6. Weekly Workflow

Every week:

1. Update ETF prices and portfolio returns.
2. Update 1M/3M/6M returns for held ETFs and reserve ETFs.
3. Check 20D/60D trend status.
4. Check drawdown from 60D high.
5. Update macro notes: Fed, BOK, CPI, oil, USD/KRW, Korea exports.
6. Update Korea flow overlay where available.
7. Score clusters.
8. Assign Add/Hold/Watch/Cut action.
9. Record any replacement decision and rationale.

## 7. Monthly Workflow

Every month:

1. Reclassify macro regime.
2. Recompute cluster ranking.
3. Compare current portfolio to target portfolio.
4. Propose trades.
5. Verify category constraints.
6. Verify monthly turnover >=10%.
7. Write monthly operating note for the competition submission.

## 8. Proposal Update Guidance

When updating the Korean investment proposal:

- Replace broad claims with the rule names from the design document.
- Correct the overseas sector allocation from the prior draft to respect the 10% cap.
- Present the initial portfolio as a table with exact ETF tickers and weights.
- Include a short constraint-check table.
- Explain why excluded assets are excluded, especially India, China, long-duration bonds, FX-only ETFs, and high yield.
- Use the scenario matrix as the risk management section.

## 9. Done Criteria

This phase is complete when:

- The design document exists and reflects the plan requirements.
- The initial portfolio totals 100%.
- All category limits pass.
- The weekly and monthly operating rules are explicit.
- The framework can be copied into the final proposal or spreadsheet without additional strategy design work.
