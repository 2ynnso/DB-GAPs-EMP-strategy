#!/usr/bin/env python3
"""Build a static GitHub Pages dashboard from the EMP framework CSV files."""

from __future__ import annotations

import csv
import html
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_DIR = ROOT / "framework"
PUBLIC_DIR = ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "index.html"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fmt_weight(value: str | float) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "-"
    return f"{number:g}%"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def build_table(rows: list[dict[str, str]], columns: list[tuple[str, str]], class_name: str = "") -> str:
    header = "".join(f"<th>{esc(label)}</th>" for key, label in columns)
    body = []
    for row in rows:
        cells = "".join(f"<td>{esc(row.get(key, ''))}</td>" for key, label in columns)
        body.append(f"<tr>{cells}</tr>")
    return f"""
      <div class="table-wrap {class_name}">
        <table>
          <thead><tr>{header}</tr></thead>
          <tbody>{''.join(body)}</tbody>
        </table>
      </div>
    """


def allocation_summary(portfolio: list[dict[str, str]]) -> dict[str, float]:
    summary = {"Risk": 0.0, "Safe": 0.0, "Total": 0.0}
    for row in portfolio:
        weight = float(row["target_weight"])
        summary[row["asset_bucket"]] += weight
        summary["Total"] += weight
    return summary


def category_summary(portfolio: list[dict[str, str]]) -> list[dict[str, str]]:
    totals: dict[str, float] = {}
    for row in portfolio:
        category = row["competition_category"]
        totals[category] = totals.get(category, 0.0) + float(row["target_weight"])
    return [
        {"category": category, "weight": fmt_weight(weight)}
        for category, weight in sorted(totals.items())
    ]


def cluster_summary(portfolio: list[dict[str, str]]) -> list[dict[str, str]]:
    totals: dict[str, float] = {}
    for row in portfolio:
        cluster = row["cluster"]
        totals[cluster] = totals.get(cluster, 0.0) + float(row["target_weight"])
    return [
        {"cluster": cluster, "weight": fmt_weight(weight)}
        for cluster, weight in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    ]


def validate(portfolio: list[dict[str, str]], etf_master: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    total_weight = sum(float(row["target_weight"]) for row in portfolio)
    if round(total_weight, 6) != 100:
        errors.append(f"initial portfolio total weight is {total_weight}, expected 100")

    selected_master = [row for row in etf_master if row["selected"] == "Y"]
    selected_weight = sum(float(row["target_weight"]) for row in selected_master)
    if len(etf_master) != 188:
        errors.append(f"ETF master has {len(etf_master)} rows, expected 188")
    if len(selected_master) != len(portfolio):
        errors.append(f"ETF master selected count is {len(selected_master)}, expected {len(portfolio)}")
    if round(selected_weight, 6) != 100:
        errors.append(f"ETF master selected total weight is {selected_weight}, expected 100")
    return errors


def render_dashboard() -> str:
    portfolio = read_csv(FRAMEWORK_DIR / "initial-portfolio.csv")
    etf_master = read_csv(FRAMEWORK_DIR / "etf-master.csv")
    weekly = read_csv(FRAMEWORK_DIR / "weekly-monitoring-dashboard.csv")
    rebalance = read_csv(FRAMEWORK_DIR / "monthly-rebalance-log.csv")
    errors = validate(portfolio, etf_master)
    if errors:
        raise SystemExit("\n".join(errors))

    summary = allocation_summary(portfolio)
    selected = [row for row in etf_master if row["selected"] == "Y"]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    category_rows = category_summary(portfolio)
    cluster_rows = cluster_summary(portfolio)

    portfolio_rows = [
        {
            "ticker": row["ticker"],
            "etf_name": row["etf_name"],
            "asset_bucket": row["asset_bucket"],
            "competition_category": row["competition_category"],
            "cluster": row["cluster"],
            "target_weight": fmt_weight(row["target_weight"]),
            "role": row["role"],
        }
        for row in portfolio
    ]

    selected_rows = [
        {
            "ticker": row["ticker"],
            "etf_name": row["etf_name"],
            "aum_krw_100m": row["aum_krw_100m"],
            "cluster": row["cluster"],
            "same_exposure_group": row["same_exposure_group"],
            "target_weight": fmt_weight(row["target_weight"]),
        }
        for row in selected
    ]

    weekly_rows = [
        {
            "cluster": row["cluster"],
            "held_tickers": row["held_tickers"],
            "target_weight": fmt_weight(row["target_weight"]),
            "decision": row["decision"],
            "proposed_action": row["proposed_action"],
            "notes": row["notes"],
        }
        for row in weekly
    ]

    rebalance_rows = [
        {
            "rebalance_date": row["rebalance_date"],
            "previous_total_risk": fmt_weight(row["previous_total_risk"]),
            "new_total_risk": fmt_weight(row["new_total_risk"]),
            "turnover": fmt_weight(row["turnover"]),
            "trigger": row["trigger"],
            "result": row["result"],
        }
        for row in rebalance
    ]

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DB GAPS EMP Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #151923;
      --muted: #687386;
      --line: #d9dee7;
      --accent: #174ea6;
      --risk: #b42318;
      --safe: #067647;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 28px 24px 18px;
      background: #fff;
      border-bottom: 1px solid var(--line);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1, h2 {{
      margin: 0;
      line-height: 1.2;
    }}
    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 18px; margin-bottom: 12px; }}
    p {{ margin: 8px 0 0; color: var(--muted); }}
    section {{ margin-bottom: 24px; }}
    .hero {{
      max-width: 1180px;
      margin: 0 auto;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
    }}
    .label {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .value {{
      margin-top: 6px;
      font-size: 24px;
      font-weight: 700;
    }}
    .risk {{ color: var(--risk); }}
    .safe {{ color: var(--safe); }}
    .table-wrap {{
      overflow-x: auto;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 760px;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      white-space: nowrap;
    }}
    th {{
      background: #f0f3f8;
      color: #3d4758;
      font-weight: 700;
      font-size: 12px;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    .note {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
    }}
    @media (max-width: 840px) {{
      header {{ padding: 22px 16px 14px; }}
      main {{ padding: 16px; }}
      .cards, .grid-2 {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="hero">
      <h1>DB GAPS EMP Dashboard</h1>
      <p>ETF Managed Portfolio framework for June-August 2026. Generated by GitHub Actions at {esc(generated_at)}.</p>
    </div>
  </header>
  <main>
    <section class="cards" aria-label="Portfolio summary">
      <div class="card"><div class="label">Risk Assets</div><div class="value risk">{fmt_weight(summary["Risk"])}</div></div>
      <div class="card"><div class="label">Safe Assets</div><div class="value safe">{fmt_weight(summary["Safe"])}</div></div>
      <div class="card"><div class="label">Total Weight</div><div class="value">{fmt_weight(summary["Total"])}</div></div>
      <div class="card"><div class="label">ETF Universe</div><div class="value">{len(etf_master)}</div></div>
    </section>

    <section>
      <h2>Initial Portfolio</h2>
      {build_table(portfolio_rows, [
        ("ticker", "Ticker"),
        ("etf_name", "ETF"),
        ("asset_bucket", "Bucket"),
        ("competition_category", "Category"),
        ("cluster", "Cluster"),
        ("target_weight", "Weight"),
        ("role", "Role"),
      ])}
    </section>

    <section class="grid-2">
      <div>
        <h2>Cluster Weights</h2>
        {build_table(cluster_rows, [("cluster", "Cluster"), ("weight", "Weight")])}
      </div>
      <div>
        <h2>Category Usage</h2>
        {build_table(category_rows, [("category", "Category"), ("weight", "Weight")])}
      </div>
    </section>

    <section>
      <h2>Selected ETF Master</h2>
      {build_table(selected_rows, [
        ("ticker", "Ticker"),
        ("etf_name", "ETF"),
        ("aum_krw_100m", "AUM(억원)"),
        ("cluster", "Cluster"),
        ("same_exposure_group", "Exposure Group"),
        ("target_weight", "Weight"),
      ])}
      <div class="note">Full 188-row ETF master is stored at framework/etf-master.csv.</div>
    </section>

    <section>
      <h2>Weekly Monitoring</h2>
      {build_table(weekly_rows, [
        ("cluster", "Cluster"),
        ("held_tickers", "Held Tickers"),
        ("target_weight", "Target"),
        ("decision", "Decision"),
        ("proposed_action", "Action"),
        ("notes", "Notes"),
      ])}
    </section>

    <section>
      <h2>Rebalance Log</h2>
      {build_table(rebalance_rows, [
        ("rebalance_date", "Date"),
        ("previous_total_risk", "Previous Risk"),
        ("new_total_risk", "New Risk"),
        ("turnover", "Turnover"),
        ("trigger", "Trigger"),
        ("result", "Result"),
      ])}
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    PUBLIC_DIR.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(render_dashboard(), encoding="utf-8")
    print(f"wrote={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
