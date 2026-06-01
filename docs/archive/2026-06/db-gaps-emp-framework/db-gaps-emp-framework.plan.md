# db-gaps-emp-framework - Plan Document

> Version: 1.0.0 | Date: 2026-05-31 | Status: Draft
> Level: Starter

---

## 1. Overview

### 1.1 Purpose

This plan defines an ETF Managed Portfolio (EMP) framework for the DB GAPS ETF Investment Competition.

The primary objective is to maximize absolute cumulative return during the June-August 2026 competition period. Sharpe ratio, volatility minimization, and benchmark-relative performance are secondary reference metrics, not the main objective.

The framework is intended for the internal team making real portfolio decisions. It must therefore provide executable allocation, monitoring, and rotation rules rather than only a polished investment proposal narrative.

### 1.2 Background

The strategy will operate only within the provided ETF universe:

`/Users/2ys/Desktop/DB Gaps/제12회_GAPS_ETF_리스트_(v260509).xlsx_-_ETF.csv`

The competition imposes the following key constraints:

- Individual ETF maximum weight: 20%
- Total risk assets: 70% or less
- Safe assets: approximately 30%
- Domestic Equity Index: 30% or less
- Domestic Equity Sector: 15% or less
- Global Equity Index: 30% or less
- Global Equity Sector: 10% or less
- FX & Commodities: 20% or less
- Domestic Bond Aggregate: 50% or less
- Domestic Corporate Bond: 30% or less
- Global Bond Aggregate: 50% or less
- Global Corporate Bond: 30% or less
- Money Market / Short Duration: 50% or less
- Initial turnover within five business days: 80% or more
- Monthly turnover: 10% or more
- Cumulative three-month turnover limit: none

The selected strategy architecture is an A+C hybrid:

- A: concentrated thematic rotation
- C: macro scenario switching

Risk assets will be concentrated in high-conviction ETF clusters such as AI & Semiconductors, Power Infrastructure, Defense, Shipbuilding, Gold, Financials, India, and selected equity index exposures. Macro scenario switching will determine when to maintain, reduce, or replace these clusters.

## 2. Goals

### 2.1 Primary Goals

- [ ] Maximize absolute cumulative portfolio return over June-August 2026.
- [ ] Use the risk asset allowance close to the 70% limit unless a clear Bear Case signal emerges.
- [ ] Identify and allocate to the strongest ETF clusters during the competition window.
- [ ] Apply a repeatable dual momentum process using macro regime, relative strength, trend, and flow indicators.
- [ ] Maintain monthly turnover of at least 10%.
- [ ] Monitor the portfolio weekly and allow conditional intra-month replacement.
- [ ] Assess current momentum strength and high-point risk every week.
- [ ] Produce an exact recommended portfolio as of June 1, 2026.

### 2.2 Non-Goals

- The framework will not optimize for Sharpe ratio.
- The framework will not build a long-term conservative EMP.
- The framework will not use machine learning return prediction.
- The framework will not use mean-variance optimization as the core construction method.
- The framework will not create detailed reports for every ETF in the universe.
- The framework will not trade individual stocks.
- Samsung Electronics and SK hynix flow data will not be used as direct trading signals.

## 3. Scope

### 3.1 In Scope

- Analyze the competition structure and portfolio constraints.
- Analyze the provided ETF universe and map ETFs to competition categories.
- Select ETFs only from the provided universe file.
- Prefer the larger AUM ETF when multiple ETFs provide the same or highly similar exposure.
- Define a June-August 2026 macro regime framework.
- Challenge and update the initial macro assumptions.
- Define strategic anchor allocation.
- Define ETF cluster groups.
- Rank clusters by expected attractiveness.
- Build a complete anchor portfolio with asset class, target weight, ETF candidate, and investment thesis.
- Design a dual momentum overlay.
- Include signal calculation, buy conditions, sell conditions, and rebalancing rules.
- Incorporate foreign and institutional flow for Korean ETFs where useful.
- Design a monthly monitoring dashboard.
- Include weekly monitoring for macro, momentum, flow, risk, and high-point assessment.
- Provide Bull, Base, and Bear scenarios with winners, losers, and portfolio adjustments.
- Provide final recommended portfolio weights as of June 1, 2026.

### 3.2 Out of Scope

- Daily automated rebalancing.
- Full automation of all ETF scoring calculations.
- Machine learning models.
- Detailed VaR/CVaR portfolio optimization, except as optional risk reference.
- Broad diversification for its own sake.
- Portfolio construction that materially underuses the 70% risk asset limit without a Bear Case trigger.

## 4. Requirements

### 4.1 Functional Requirements

1. ETF universe restriction
   - All selected ETFs must come from the provided ETF universe file.

2. Same-exposure ETF selection rule
   - If multiple ETFs provide the same or similar index, theme, or asset exposure, the larger AUM ETF should be selected by default.
   - A smaller AUM ETF may be selected only if its exposure is materially more direct or more suitable for the thesis.

3. Asset constraint compliance
   - Total risk assets must remain at or below 70%.
   - Safe assets should remain approximately 30%.
   - Each ETF must remain at or below 20%.
   - All detailed category limits must be respected.

4. Macro regime framework
   - The framework must evaluate AI capex, semiconductor cycle, US rates, inflation, energy and geopolitical risks, Korean exports, USD/KRW, and foreign investor flow.

5. ETF cluster construction
   - ETFs must be grouped into actionable clusters such as AI & Semiconductors, Power Infrastructure, Defense, Shipbuilding, Gold, Financials, India, and Bonds.

6. Cluster attractiveness ranking
   - Clusters must be ranked using macro fit, price momentum, flow sensitivity, and downside risk.

7. Dual momentum
   - The framework must combine absolute momentum and relative momentum.
   - Signals may include 1-month, 3-month, and 6-month returns, trend filters, and relative strength.

8. Korean ETF flow overlay
   - For domestic equity and sector ETFs, foreign and institutional flow should be used as an overlay.
   - Primary flow indicators should be ETF-level and sector-level where available.
   - Samsung Electronics and SK hynix foreign flow may be used only as a supplementary proxy for domestic semiconductor ETF direction.

9. Monthly rebalancing
   - The framework must include a monthly regular rebalance and ensure the monthly 10% turnover requirement can be met.

10. Weekly monitoring
   - The framework must include weekly monitoring of macro regime, cluster momentum, ETF relative strength, flow, FX, rates, commodities, drawdown, current momentum score, and high-point risk.
   - If conditions are triggered, intra-month replacement is allowed.

11. Scenario response
   - Bull, Base, and Bear scenarios must define expected winners, expected losers, and portfolio adjustment rules.

12. Final portfolio
   - The final output must provide exact target weights as of June 1, 2026.

### 4.2 Non-Functional Requirements

- Explainability: Every holding must have a clear investment rationale.
- Execution practicality: The team must be able to update the framework using ETF prices, AUM, volume, macro data, and flow data.
- Concentration: The framework should prioritize high-conviction clusters over broad diversification.
- Rule-based discipline: Discretion is allowed, but buy, sell, and replacement decisions must be tied to predefined rules.
- Liquidity preference: Larger AUM ETFs are preferred for similar exposure.
- Competition fit: The strategy must be aggressive and dynamic enough for a three-month return competition.

## 5. Success Criteria

- [ ] The final portfolio uses the ETF universe correctly and violates no competition constraints.
- [ ] The final framework prioritizes absolute cumulative return over Sharpe ratio.
- [ ] The strategy uses approximately 70% risk assets and 30% safe assets in the Base Case.
- [ ] The portfolio contains concentrated exposure to the highest-ranked clusters.
- [ ] Each ETF has a clear thesis tied to macro, momentum, flow, or risk budgeting.
- [ ] Monthly turnover of at least 10% can be achieved through justified rotation.
- [ ] Weekly monitoring can identify whether current momentum is strengthening, fading, or at high-point reversal risk.
- [ ] Buy, sell, and replacement rules are explicit enough for the team to execute.
- [ ] Bull, Base, and Bear scenario adjustments are defined before the competition starts.
- [ ] Exact target weights are produced for June 1, 2026.

## 6. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Concentrated theme reversal | High | Medium | Respect individual ETF and cluster limits; monitor momentum weekly; reduce exposure after trend breakdown or high-point failure |
| Macro assumption error | High | Medium | Define Bull/Base/Bear scenarios; re-rank clusters when two or more macro indicators reverse |
| Momentum chase near high point | High | Medium | Combine 1M, 3M, 6M returns with trend, drawdown from recent high, moving average distance, and flow |
| Monthly turnover miss | High | Low | Predefine at least 10% monthly rotation candidates |
| Liquidity and execution risk | Medium | Medium | Prefer larger AUM ETFs for similar exposure; limit smaller niche ETFs |
| Safe asset return drag | Medium | High | Rotate safe assets across money market, domestic bonds, US bonds, and credit depending on rate regime |
| Korean market flow reversal | High | Medium | Track ETF momentum, sector foreign/institutional flow, KOSPI/KOSDAQ foreign flow, USD/KRW, and semiconductor export indicators |

## 7. Architecture Considerations

The EMP framework will operate through seven layers:

1. Input Layer
   - ETF universe file
   - ETF price data
   - ETF AUM and trading value
   - ETF index and category classification
   - Macro data
   - Korean market flow data
   - Supplementary semiconductor proxy data

2. Classification Layer
   - Competition category
   - Risk asset versus safe asset
   - ETF cluster
   - Same-exposure ETF group

3. Macro Regime Layer
   - AI capex
   - Semiconductor cycle
   - US rate path
   - Inflation and commodities
   - USD/KRW
   - Korean exports
   - Foreign investor flow
   - Geopolitics

4. Momentum Scoring Layer
   - Absolute momentum
   - Relative momentum
   - Trend filter
   - High-point risk
   - Flow overlay

5. Portfolio Construction Layer
   - 70% risk asset / 30% safe asset structure
   - Category limit checks
   - Cluster allocation
   - ETF selection using AUM, momentum, and direct exposure

6. Monitoring & Rebalancing Layer
   - Monthly rebalance
   - Weekly monitoring
   - Conditional intra-month replacement

7. Output Layer
   - Strategy framework
   - ETF cluster table
   - Cluster ranking
   - Anchor portfolio
   - Momentum formula
   - Monitoring dashboard
   - Scenario response table
   - Final June 1, 2026 target weights

## 8. Schedule

| Phase | Target Date | Status |
|-------|------------|--------|
| Plan | 2026-05-31 | In Progress |
| Design | 2026-05-31 | Pending |
| Implementation | TBD | Pending |
| Review | TBD | Pending |

## 9. References

- ETF universe: `/Users/2ys/Desktop/DB Gaps/제12회_GAPS_ETF_리스트_(v260509).xlsx_-_ETF.csv`
- Competition constraint screenshots provided by user
- Existing draft proposal documents in `/Users/2ys/Desktop/DB Gaps/투자계획서/`

