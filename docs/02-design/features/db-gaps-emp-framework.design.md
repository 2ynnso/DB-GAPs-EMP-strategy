# db-gaps-emp-framework - Design Document

> Version: 1.0.0 | Date: 2026-06-01 | Status: Draft  
> Level: Starter | Plan: docs/01-plan/features/db-gaps-emp-framework.plan.md

---

## 1. Overview

This document develops the prior plan into an executable ETF Managed Portfolio (EMP) framework for the DB GAPS ETF Investment Competition.

The framework is not a passive investment proposal. It is a rule-based decision system that converts macro regime, ETF universe constraints, cluster momentum, liquidity preference, flow overlay, and competition turnover requirements into a concrete portfolio and monitoring process.

Primary objective:

- Maximize absolute cumulative return during June-August 2026.

Secondary objectives:

- Keep all competition constraints satisfied.
- Keep the Base Case portfolio close to 70% risk assets and 30% safe assets.
- Rotate aggressively enough to meet turnover requirements without relying on arbitrary trades.
- Make every holding explainable through macro fit, momentum, liquidity, or hedge value.

## 2. Current Market Snapshot

As of the June 1, 2026 design cut, the working macro view is **Reflation with geopolitical risk premium**, not pure stagflation.

| Variable | Current read | Portfolio implication |
|---|---:|---|
| US CPI | April 2026 CPI-U +3.8% YoY, core +2.8% YoY | Inflation risk remains active; avoid long-duration bond concentration |
| Fed policy | Target range 3.50%-3.75% since the March 18, 2026 FOMC implementation note | Rate-cut beta is not the core thesis; favor equity earnings momentum over duration |
| Korea base rate | Bank of Korea held Base Rate at 2.50% on May 28, 2026 | Maintain short-duration domestic safe asset bucket |
| Korea CPI | April 2026 CPI +2.6% YoY | Inflation reacceleration risk supports short-duration safety and commodity hedge |
| Korea exports | May 2026 exports reported at record level, led by semiconductors | Supports Korean semiconductor, KOSPI200, and AI supply-chain exposure |
| Oil/Hormuz | Oil remains highly sensitive to Iran/Hormuz headlines; recent reports show Brent below prior spike levels but still risk-premium driven | Keep WTI hedge, but cap exposure and define fast exit rule |
| AI capex | 2026 hyperscaler capex estimates remain elevated; several 2026 outlooks point to continued AI infrastructure investment | Keep AI semiconductor and power infrastructure clusters as primary return engine |

Reference links:

- US CPI: https://www.bls.gov/news.release/cpi.nr0.htm
- Fed implementation note: https://www.federalreserve.gov/newsevents/pressreleases/monetary20260318a1.htm
- Bank of Korea May 28 decision: https://www.bok.or.kr/eng/bbs/E0000634/view.do?nttId=10098190
- Korea CPI: https://mods.go.kr/board.es?act=view&bid=11751&list_no=444937&mid=a20109020000
- Korea exports: https://koreajoongangdaily.joins.com/news/2026-06-01/business/industry/Koreas-monthly-exports-up-53-to-record-high-of-878-billion-in-May/2605422
- AI capex cycle: https://www.allianz.com/en/economic_research/insights/publications/specials_fmo/260325_ai-capex-cycle.html

## 3. System Architecture

The EMP framework operates through seven layers.

| Layer | Input | Decision output |
|---|---|---|
| 1. Universe | Competition ETF CSV, AUM, category, risk/safe label | Tradable ETF master |
| 2. Classification | Category, index, ETF name, thesis keyword | Risk bucket, competition category, cluster |
| 3. Macro Regime | CPI, rates, oil, FX, exports, earnings, flow | Bull/Base/Bear regime state |
| 4. Cluster Scoring | Macro fit, momentum, flow, liquidity, high-point risk | Ranked clusters |
| 5. ETF Selection | AUM, directness, liquidity, hedge status | Representative ETF per exposure |
| 6. Portfolio Construction | Cluster rank, category limits, risk budget | Target weights |
| 7. Monitoring | Weekly signal board, event triggers, drawdown checks | Hold, trim, replace, or rebalance |

## 4. Data Model

### 4.1 ETF Master

| Field | Description | Example |
|---|---|---|
| ticker | Competition ETF ticker | A395160 |
| name | ETF name | KODEX AI반도체 |
| aum_krw_100m | AUM in KRW 100 million | 20947 |
| index_name | Underlying index | KODEX AI semiconductor index |
| risk_label | 위험 or 안전 | 위험 |
| competition_category | Category from ETF file | 국내주식_섹터 |
| cluster | Internal strategy cluster | AI & Semiconductors |
| same_exposure_group | Comparable ETF group | Korea semiconductor |
| selected_role | Core, satellite, hedge, reserve | Core |

### 4.2 Cluster Table

| Cluster | Included exposures | Primary role |
|---|---|---|
| AI & Semiconductors | Korea AI semiconductor, US semiconductor, Nasdaq100 | Primary return engine |
| AI Power Infrastructure | US AI power infrastructure, Korea power equipment | Secondary return engine |
| Korea Cyclical Alpha | KOSPI200, shipbuilding, defense | Korea export and policy beta |
| Commodity Hedge | Gold, WTI oil | Geopolitical and inflation hedge |
| Short-Duration Safety | CD, KOFR, short monetary bonds | Volatility buffer |
| Domestic Carry | Short KTB, aggregate bonds, high-grade credit | Carry with limited duration |
| USD Safety | US dollar short bond exposure | Dollar liquidity buffer |

### 4.3 Signal Board

| Signal | Frequency | Bullish condition | Bearish condition |
|---|---|---|---|
| Absolute momentum | Weekly | 1M and 3M returns positive | 1M and 3M returns both negative |
| Relative momentum | Weekly | Cluster in top 40% of risk clusters | Cluster falls to bottom 30% |
| Trend filter | Weekly | Price above 20D and 60D moving averages | Price below 60D moving average |
| High-point risk | Weekly | Drawdown from 60D high less than 5% | Drawdown from 60D high greater than 8% with negative 1M return |
| Flow overlay | Weekly | Foreign/institutional net buying in sector or ETF | Two-week persistent net selling |
| Macro fit | Monthly/event | Regime supports cluster | Two or more macro drivers reverse |
| Liquidity | Monthly | AUM leader or high trading value | Persistent spread/tracking risk |

## 5. Scoring Framework

Cluster score is calculated on a 100-point scale.

| Component | Weight | Definition |
|---|---:|---|
| Macro fit | 30 | Whether the cluster benefits from the active macro regime |
| Relative momentum | 25 | Rank versus other risk clusters using 1M/3M/6M returns |
| Absolute momentum | 15 | Positive price trend and moving-average confirmation |
| Flow overlay | 10 | Foreign/institutional and sector flow confirmation |
| Liquidity/AUM | 10 | AUM leadership and execution practicality |
| High-point risk | 10 | Penalty for extended price, reversal candle, or drawdown pattern |

Formula:

```text
cluster_score =
  0.30 * macro_fit
+ 0.25 * relative_momentum
+ 0.15 * absolute_momentum
+ 0.10 * flow_overlay
+ 0.10 * liquidity
+ 0.10 * high_point_risk_adjusted
```

Interpretation:

| Score | Action |
|---:|---|
| 80-100 | Core overweight candidate |
| 65-79 | Hold or modest overweight |
| 50-64 | Neutral or reserve only |
| 35-49 | Underweight or reduce |
| 0-34 | Exclude unless hedge role is explicit |

## 6. ETF Selection Rules

1. ETF must exist in the competition universe CSV.
2. Same-exposure groups default to the larger AUM ETF.
3. Smaller AUM ETF can override only when exposure is materially more direct.
4. Individual ETF target weight must be 20% or less.
5. Competition category limits must be checked after every rebalance.
6. Risk asset bucket must be 70% or less.
7. Base Case safe asset bucket should remain near 30%.
8. Overseas bond exposure should avoid long duration unless a clear rate-cut regime appears.
9. WTI oil is treated as tactical hedge, not a permanent strategic holding.
10. Gold is treated as tail hedge and currency/inflation diversifier.

## 7. Initial Portfolio - June 1, 2026 Base Case

The initial target portfolio uses the 70% risk asset budget fully, while keeping every category and individual ETF below its stated limit.

### 7.1 Risk Assets - 70%

| Category | Ticker | ETF | Weight | Thesis |
|---|---|---|---:|---|
| 국내주식_지수 | A069500 | KODEX 200 | 10% | Broad Korea beta; semiconductor-led KOSPI earnings momentum |
| 국내주식_섹터 | A395160 | KODEX AI반도체 | 8% | Direct Korea AI semiconductor/HBM exposure |
| 국내주식_섹터 | A466920 | SOL 조선TOP3플러스 | 4% | Export, defense-adjacent, and order-cycle alpha |
| 국내주식_섹터 | A449450 | PLUS K방산 | 3% | Geopolitical risk premium and policy demand |
| 해외주식_지수 | A360750 | TIGER 미국S&P500 | 13% | Broad US quality/earnings exposure |
| 해외주식_지수 | A133690 | TIGER 미국나스닥100 | 12% | AI platform and growth exposure |
| 해외주식_섹터 | A497570 | TIGER 미국필라델피아AI반도체나스닥 | 6% | US AI semiconductor supply chain |
| 해외주식_섹터 | A487230 | KODEX 미국AI전력핵심인프라 | 4% | AI data-center power infrastructure |
| FX 및 원자재 | A411060 | ACE KRX금현물 | 6% | Geopolitical and inflation hedge |
| FX 및 원자재 | A261220 | KODEX WTI원유선물(H) | 4% | Hormuz/oil shock hedge; capped due to binary reversal risk |

### 7.2 Safe Assets - 30%

| Category | Ticker | ETF | Weight | Thesis |
|---|---|---|---:|---|
| 금리연계형/초단기채권 | A459580 | KODEX CD금리액티브(합성) | 8% | Highest-liquidity rate-linked cash proxy |
| 금리연계형/초단기채권 | A423160 | KODEX KOFR금리액티브(합성) | 5% | Overnight-rate linked buffer |
| 국내채권_종합 | A157450 | TIGER 단기통안채 | 4% | Short-duration domestic safety |
| 국내채권_종합 | A114260 | KODEX 국고채3년 | 3% | Limited-duration KTB exposure |
| 국내채권_회사채 | A273130 | KODEX 종합채권(AA-이상)액티브 | 6% | High-grade carry |
| 해외채권_종합 | A329750 | TIGER 미국달러단기채권액티브 | 4% | USD short-bond liquidity and currency buffer |

### 7.3 Constraint Check

| Constraint | Limit | Portfolio value | Status |
|---|---:|---:|---|
| Individual ETF | <=20% | max 13% | Pass |
| Total risk assets | <=70% | 70% | Pass |
| Safe assets | about 30% | 30% | Pass |
| Domestic equity index | <=30% | 10% | Pass |
| Domestic equity sector | <=15% | 15% | Pass |
| Global equity index | <=30% | 25% | Pass |
| Global equity sector | <=10% | 10% | Pass |
| FX & commodities | <=20% | 10% | Pass |
| Domestic bond aggregate | <=50% | 7% | Pass |
| Domestic corporate bond | <=30% | 6% | Pass |
| Global bond aggregate | <=50% | 4% | Pass |
| Money market / short duration | <=50% | 13% | Pass |

## 8. Rebalancing Rules

### 8.1 Monthly Regular Rebalance

Timing:

- First trading day of each month during June-August 2026.

Required actions:

1. Recompute macro regime.
2. Recompute cluster scores.
3. Re-rank risk clusters.
4. Check category and individual ETF limits.
5. Rotate at least 10% of portfolio weight if the required monthly turnover is not naturally met.
6. Document all weight changes in the monthly operating note.

Monthly turnover candidates:

| If condition occurs | Rotate from | Rotate to | Minimum turnover |
|---|---|---|---:|
| AI capex momentum remains strong | S&P500 or safe asset | AI semiconductor/power cluster | 5%-10% |
| Oil deal/Hormuz reopening confirmed | WTI oil | S&P500, Nasdaq100, or short bond | 4% |
| Fed turns more hawkish | Nasdaq100, US semiconductor, KTB 3Y | CD/KOFR, short bonds, gold | 5%-12% |
| Korean foreign flow weakens | KODEX 200 or Korea sector | S&P500, gold, CD/KOFR | 5%-10% |
| Korea semiconductor flow strengthens | KODEX 200 or safe asset | KODEX AI반도체 | 3%-7% |

### 8.2 Weekly Monitoring

Every week, classify each cluster as **Add / Hold / Watch / Cut**.

| Decision | Rule |
|---|---|
| Add | Score >=80 and no category limit breach |
| Hold | Score 65-79 or hedge role remains valid |
| Watch | Score 50-64, extended high-point risk, or mixed flow |
| Cut | Score <50, trend breakdown, or macro thesis invalidated |

### 8.3 Intra-Month Replacement

Intra-month replacement is allowed when one of the following triggers occurs:

- ETF closes below 60D moving average for two consecutive trading days.
- 1M return turns negative and drawdown from 60D high exceeds 8%.
- Two or more macro regime drivers reverse at the same time.
- Foreign/institutional flow turns persistently negative for two weeks in the relevant Korean cluster.
- Oil ceasefire or Hormuz reopening removes the WTI hedge thesis.
- AI capex/earnings guidance materially disappoints during July earnings season.

## 9. Scenario Matrix

| Scenario | Probability | Winners | Losers | Portfolio response |
|---|---:|---|---|---|
| Bull: Reflation + AI capex confirmation | 30% | AI semis, Nasdaq100, KOSPI200, power infra | Gold, cash-like assets | Add 5%-10% to AI/US growth from safe asset and gold, while staying within category limits |
| Base: Reflation + geopolitical premium | 45% | AI semis, US index, Korea exporters, gold/oil hedge | Long duration bonds | Maintain 70/30, keep WTI capped, rebalance monthly |
| Bear: Oil shock + Fed/BOK hawkish + equity reversal | 25% | CD/KOFR, short bonds, gold, USD short bond | Nasdaq, semis, KOSPI cyclicals | Cut risk assets by 10%-15%, add to short-duration safety and gold |

## 10. Monitoring Dashboard Design

The dashboard should be maintained in a table or spreadsheet. Automation is optional, but the structure must be consistent.

| Section | Metrics |
|---|---|
| Portfolio | Weight, P/L, category usage, risk/safe split |
| Macro | US CPI, Fed path, Korea CPI, BOK decision, oil, USD/KRW, exports |
| Momentum | 1M/3M/6M return, 20D/60D trend, relative rank |
| Flow | Korea foreign flow, institutional flow, sector flow, ETF flow where available |
| Risk | Drawdown from high, volatility proxy, high-point warning |
| Actions | Add/Hold/Watch/Cut, proposed turnover, rationale |

## 11. Implementation Order

1. Create ETF master from the competition universe CSV.
2. Add internal cluster mapping and same-exposure groups.
3. Build the initial portfolio table and category constraint checker.
4. Build weekly monitoring table.
5. Build monthly rebalance log.
6. Produce final investment proposal language from the framework.
7. During the competition, update signals weekly and rebalance monthly.

## 12. Design Decisions

| Decision | Rationale |
|---|---|
| Use 70% risk assets in Base Case | The competition rewards absolute return, and the plan explicitly prioritizes return over Sharpe ratio |
| Cap overseas sector at 10% | The prior draft's 18% overseas sector allocation conflicts with the stated category limit |
| Keep Korea sector at exactly 15% | Uses full thematic limit while respecting category cap |
| Use gold and WTI together | Gold protects tail risk; WTI targets the specific oil/Hormuz shock |
| Use short-duration safety | Rate-cut conviction is insufficient; long-duration bonds carry asymmetric drawdown risk |
| Prefer AUM leaders | Competition execution and tracking practicality matter |

## 13. Open Items

- Add actual ETF price return data for 1M/3M/6M momentum once data source is selected.
- Add weekly foreign/institutional flow source for Korea sector clusters.
- Confirm whether competition category limits are hard-coded exactly as listed in the plan.
- Convert this design into a spreadsheet or script if the team wants automated weekly updates.
