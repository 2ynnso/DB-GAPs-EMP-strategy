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
MOMENTUM_OUTPUT_PATH = PUBLIC_DIR / "momentum.html"


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


BUCKET_LABELS = {
    "Risk": "위험자산",
    "Safe": "안전자산",
}

DECISION_LABELS = {
    "Add": "확대",
    "Hold": "유지",
    "Watch": "관찰",
    "Cut": "축소",
}

CLUSTER_NOTES = {
    "AI & Semiconductors": "핵심 수익 엔진. AI 설비투자와 반도체 사이클 확인 필요.",
    "AI Power Infrastructure": "AI 데이터센터 전력 인프라 수혜 후보.",
    "Korea Cyclical Alpha": "한국 수출, 조선, 방산 모멘텀 점검 대상.",
    "Core Equity Beta": "한국/미국 핵심 지수 노출.",
    "Commodity Hedge": "지정학 및 인플레이션 헤지. 유가 뉴스 확인 필요.",
    "Short-Duration Safety": "변동성 완충 및 리밸런싱 재원.",
    "Domestic Carry": "국내 단기채와 우량채 캐리. BOK 확인 필요.",
    "USD Safety": "달러 단기채 완충. USD/KRW와 미국 금리 확인 필요.",
}

THESIS_KO = {
    "A069500": "반도체 중심 코스피 이익 모멘텀",
    "A395160": "국내 AI 반도체와 HBM 직접 노출",
    "A466920": "수출과 방산 인접 조선 업황 수혜",
    "A449450": "지정학 리스크와 방산 정책 수요",
    "A360750": "미국 대형 우량주와 이익 모멘텀",
    "A133690": "AI 플랫폼과 미국 성장주 노출",
    "A497570": "미국 AI 반도체 밸류체인",
    "A487230": "AI 데이터센터 전력 인프라 수혜",
    "A411060": "지정학과 인플레이션 헤지",
    "A261220": "유가 급등과 호르무즈 리스크 헤지",
    "A459580": "고유동성 CD금리형 현금성 자산",
    "A423160": "KOFR 연동 초단기 변동성 완충",
    "A157450": "짧은 듀레이션 국내 안전자산",
    "A114260": "제한적 듀레이션 국고채 노출",
    "A273130": "AA- 이상 우량채 캐리",
    "A329750": "달러 단기채와 환율 완충",
}

TRIGGER_KO = {
    "A069500": "외국인 수급이 2주 연속 약화되면 축소 검토",
    "A395160": "섹터 수급과 1개월 모멘텀이 개선되면 확대 검토",
    "A466920": "상대순위가 하위 30%로 하락하면 축소",
    "A449450": "지정학 프리미엄 약화와 추세 이탈 동시 발생 시 축소",
    "A360750": "AI 모멘텀 강화 시 일부를 테마 ETF 확대 재원으로 사용",
    "A133690": "Fed 매파 충격이 성장주에 부담이면 축소",
    "A497570": "7월 실적/AI capex 가이던스 훼손 시 축소",
    "A487230": "AI capex 사이클이 유지되면 보유",
    "A411060": "위험자산 강세가 확인되면 일부 축소",
    "A261220": "종전 또는 호르무즈 재개방 확인 시 청산",
    "A459580": "Fed/BOK 매파 충격 시 확대",
    "A423160": "위험 클러스터 점수 50 미만 시 확대",
    "A157450": "더 나은 초단기 대안이 없으면 유지",
    "A114260": "BOK 인상 신호 강화 시 축소",
    "A273130": "크레딧 스프레드 확대 시 축소",
    "A329750": "달러 헤지 필요성이 유지되면 보유",
}

ACTION_KO = {
    "Update signals weekly": "주간 수익률, 추세, 수급 값 입력 필요",
    "Update oil and gold thesis weekly": "유가, 금, 지정학 뉴스 주간 점검 필요",
    "Use as rebalance source or risk buffer": "리밸런싱 재원 또는 위험 완충으로 활용",
    "Watch BOK and credit spreads": "BOK 결정과 크레딧 스프레드 확인",
    "Watch USD/KRW and US rate shock": "USD/KRW와 미국 금리 충격 확인",
    "Positive momentum confirmed; review category limits before adding": "모멘텀 양호. 한도 확인 후 확대 검토",
    "Momentum acceptable; keep current allocation": "모멘텀 유지. 현재 비중 유지",
    "Momentum mixed; review next weekly update before trading": "모멘텀 혼조. 다음 주 확인 전까지 관찰",
    "Momentum weak; prepare reduction or replacement candidate": "모멘텀 약화. 축소 또는 대체 후보 준비",
}


def bucket_label(value: str) -> str:
    return BUCKET_LABELS.get(value, value)


def decision_label(value: str) -> str:
    return DECISION_LABELS.get(value, value or "미정")


def action_label(value: str) -> str:
    return ACTION_KO.get(value, value or "업데이트 필요")


def empty(value: str | None) -> bool:
    return value is None or value.strip() == ""


def momentum_status(row: dict[str, str]) -> str:
    fields = [
        "one_month_return",
        "three_month_return",
        "six_month_return",
        "above_20d_ma",
        "above_60d_ma",
        "drawdown_from_60d_high",
        "relative_rank",
        "cluster_score",
    ]
    if all(empty(row.get(field)) for field in fields):
        return "모멘텀 미입력"
    if any(empty(row.get(field)) for field in fields):
        return "일부 업데이트 필요"
    return "업데이트 완료"


def dashboard_status(weekly: list[dict[str, str]]) -> tuple[str, str]:
    statuses = [momentum_status(row) for row in weekly]
    if all(status == "업데이트 완료" for status in statuses):
        return "모멘텀 확인 완료", "주간 모멘텀과 추세 필드가 모두 입력되어 있습니다."
    if any(status == "일부 업데이트 필요" for status in statuses):
        return "모멘텀 일부 확인", "일부 클러스터의 수익률, 추세, 점수 필드가 비어 있습니다."
    return "모멘텀 미확인", "현재 CSV에는 1M/3M/6M 수익률과 추세 값이 비어 있습니다. GitHub Actions 자동 업데이트 실행이 필요합니다."


def latest_price_date(weekly: list[dict[str, str]]) -> str:
    dates = sorted({row.get("price_data_as_of", "") for row in weekly if row.get("price_data_as_of", "")})
    return dates[-1] if dates else "미수집"


def status_class(status: str) -> str:
    if status == "업데이트 완료":
        return "ok"
    if status == "일부 업데이트 필요":
        return "warn"
    return "missing"


def decision_class(decision: str) -> str:
    return {
        "Add": "ok",
        "Hold": "neutral",
        "Watch": "warn",
        "Cut": "missing",
    }.get(decision, "neutral")


def parse_percent(value: str) -> float:
    try:
        return float(value.replace("%", "").strip())
    except (AttributeError, ValueError):
        return 0.0


def parse_score(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def build_table(rows: list[dict[str, str]], columns: list[tuple[str, str]], class_name: str = "") -> str:
    header = "".join(f"<th>{esc(label)}</th>" for key, label in columns)
    body = []
    for row in rows:
        cells = ""
        for key, label in columns:
            value = row.get(key, "")
            if key == "momentum_status":
                cells += f'<td><span class="badge {esc(row.get("status_class", ""))}">{esc(value)}</span></td>'
            elif key in {"decision", "opportunity"}:
                cells += f'<td><span class="badge {esc(row.get("decision_class", ""))}">{esc(value)}</span></td>'
            else:
                cells += f"<td>{esc(value)}</td>"
        body.append(f"<tr>{cells}</tr>")
    return f"""
      <div class="table-wrap {class_name}">
        <table>
          <thead><tr>{header}</tr></thead>
          <tbody>{''.join(body)}</tbody>
        </table>
      </div>
    """


def base_css(table_min_width: int = 760) -> str:
    return f"""
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #151923;
      --muted: #667085;
      --line: #e3e7ee;
      --line-strong: #cdd5e1;
      --accent: #1f5f99;
      --accent-soft: #eef5ff;
      --risk: #b42318;
      --safe: #067647;
      --warn: #b54708;
      --missing: #7a271a;
      --shadow: 0 10px 28px rgba(15, 23, 42, .06);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(31, 95, 153, .10), transparent 30rem),
        var(--bg);
      color: var(--text);
      font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 28px 24px 22px;
      background: rgba(255, 255, 255, .92);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(10px);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1, h2 {{ margin: 0; line-height: 1.2; letter-spacing: 0; }}
    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 18px; margin-bottom: 12px; }}
    p {{ margin: 8px 0 0; color: var(--muted); }}
    a {{ color: var(--accent); font-weight: 700; text-decoration: none; }}
    section {{ margin-bottom: 22px; }}
    .hero {{
      max-width: 1180px;
      margin: 0 auto;
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 20px;
    }}
    .hero-copy {{ max-width: 760px; }}
    .nav-pills {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .nav-pills a {{
      display: inline-flex;
      align-items: center;
      min-height: 34px;
      padding: 7px 12px;
      border: 1px solid var(--line-strong);
      border-radius: 999px;
      background: #fff;
      color: #344054;
      box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
    }}
    .nav-pills a.active {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }}
    .status-panel {{
      display: grid;
      grid-template-columns: 1.25fr .75fr;
      gap: 16px;
      margin-bottom: 20px;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    .guide {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .card, .panel, .table-wrap {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .card {{ padding: 14px 16px; }}
    .panel {{ padding: 18px; }}
    .panel strong {{ display: block; font-size: 20px; margin-bottom: 6px; }}
    .panel ul {{ margin: 12px 0 0; padding-left: 18px; color: var(--muted); }}
    .panel li {{ margin: 4px 0; }}
    .label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .value {{
      margin-top: 6px;
      font-size: 24px;
      font-weight: 800;
    }}
    .risk {{ color: var(--risk); }}
    .safe {{ color: var(--safe); }}
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
      background: #edf2f7;
      color: #344054;
      white-space: nowrap;
    }}
    .badge.ok {{ background: #ecfdf3; color: var(--safe); }}
    .badge.warn {{ background: #fffaeb; color: var(--warn); }}
    .badge.missing {{ background: #fef3f2; color: var(--missing); }}
    .badge.neutral {{ background: var(--accent-soft); color: var(--accent); }}
    .table-wrap {{ overflow-x: auto; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: {table_min_width}px;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      white-space: normal;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #f8fafc;
      color: #475467;
      font-weight: 800;
      font-size: 12px;
      z-index: 1;
    }}
    tbody tr:nth-child(even) {{ background: #fbfcfe; }}
    tr:last-child td {{ border-bottom: 0; }}
    .note {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
    }}
    .priority {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 12px;
    }}
    .priority-item {{
      background: #f8fafc;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }}
    .priority-item b, .guide b {{ display: block; margin-bottom: 4px; }}
    @media (max-width: 840px) {{
      header {{ padding: 22px 16px 14px; }}
      main {{ padding: 16px; }}
      .hero {{ align-items: flex-start; flex-direction: column; }}
      .cards, .grid-2, .status-panel, .priority, .guide {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 24px; }}
    }}
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
    status_title, status_detail = dashboard_status(weekly)
    monitoring_ready = sum(1 for row in weekly if momentum_status(row) == "업데이트 완료")
    monitoring_total = len(weekly)
    price_data_as_of = latest_price_date(weekly)

    category_rows = category_summary(portfolio)
    cluster_rows = cluster_summary(portfolio)

    portfolio_rows = [
        {
            "ticker": row["ticker"],
            "etf_name": row["etf_name"],
            "asset_bucket": bucket_label(row["asset_bucket"]),
            "competition_category": row["competition_category"],
            "cluster": row["cluster"],
            "target_weight": fmt_weight(row["target_weight"]),
            "role": row["role"],
            "thesis": THESIS_KO.get(row["ticker"], row["thesis"]),
            "action_trigger": TRIGGER_KO.get(row["ticker"], row["action_trigger"]),
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
            "one_month_return": row.get("one_month_return", ""),
            "three_month_return": row.get("three_month_return", ""),
            "six_month_return": row.get("six_month_return", ""),
            "above_20d_ma": row.get("above_20d_ma", ""),
            "above_60d_ma": row.get("above_60d_ma", ""),
            "drawdown_from_60d_high": row.get("drawdown_from_60d_high", ""),
            "relative_rank": row.get("relative_rank", ""),
            "cluster_score": row.get("cluster_score", ""),
            "momentum_status": momentum_status(row),
            "decision": decision_label(row["decision"]),
            "proposed_action": action_label(row["proposed_action"]),
            "notes": row["notes"] or CLUSTER_NOTES.get(row["cluster"], ""),
            "status_class": status_class(momentum_status(row)),
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
{base_css()}
  </style>
</head>
<body>
  <header>
    <div class="hero">
      <div class="hero-copy">
        <h1>DB GAPS EMP 운용 대시보드</h1>
        <p>2026년 6-8월 ETF EMP 전략 현황입니다. GitHub Actions 생성 시각: {esc(generated_at)}.</p>
      </div>
      <nav class="nav-pills" aria-label="dashboard navigation">
        <a class="active" href="index.html">종합</a>
        <a href="momentum.html">주식 모멘텀</a>
      </nav>
    </div>
  </header>
  <main>
    <section class="status-panel" aria-label="현재 상황">
      <div class="panel">
        <strong>현재 상황: 기준 포트폴리오 구축 완료, 자동 모멘텀 업데이트 작동 중</strong>
        <p>초기 포트폴리오는 위험자산 70%, 안전자산 30%로 제약 조건을 통과했습니다. 모멘텀 값은 GitHub Actions가 가격 API에서 자동 수집해 갱신합니다.</p>
        <div class="priority">
          <div class="priority-item"><b>1. 먼저 확인</b>1M/3M/6M 수익률, 20D/60D 추세</div>
          <div class="priority-item"><b>2. 다음 확인</b>외국인/기관 수급, USD/KRW, 유가</div>
          <div class="priority-item"><b>3. 행동 판단</b>확대/유지/관찰/축소로 클러스터 판정</div>
        </div>
      </div>
      <div class="panel">
        <strong>{esc(status_title)}</strong>
        <p>{esc(status_detail)}</p>
        <ul>
          <li>모니터링 완료 클러스터: {monitoring_ready}/{monitoring_total}</li>
          <li>가격 데이터 기준일: {esc(price_data_as_of)}</li>
          <li>대시보드는 repository CSV 기준으로만 표시됩니다.</li>
        </ul>
      </div>
    </section>

    <section class="cards" aria-label="Portfolio summary">
      <div class="card"><div class="label">위험자산</div><div class="value risk">{fmt_weight(summary["Risk"])}</div></div>
      <div class="card"><div class="label">안전자산</div><div class="value safe">{fmt_weight(summary["Safe"])}</div></div>
      <div class="card"><div class="label">총 비중</div><div class="value">{fmt_weight(summary["Total"])}</div></div>
      <div class="card"><div class="label">ETF 유니버스</div><div class="value">{len(etf_master)}</div></div>
    </section>

    <section>
      <h2>초기 포트폴리오</h2>
      {build_table(portfolio_rows, [
        ("ticker", "티커"),
        ("etf_name", "ETF"),
        ("asset_bucket", "자산구분"),
        ("competition_category", "대회분류"),
        ("cluster", "전략 클러스터"),
        ("target_weight", "비중"),
        ("thesis", "편입 논리"),
        ("action_trigger", "점검 트리거"),
      ])}
    </section>

    <section class="grid-2">
      <div>
        <h2>클러스터별 비중</h2>
        {build_table(cluster_rows, [("cluster", "전략 클러스터"), ("weight", "비중")])}
      </div>
      <div>
        <h2>대회 분류별 사용 현황</h2>
        {build_table(category_rows, [("category", "대회분류"), ("weight", "비중")])}
      </div>
    </section>

    <section>
      <h2>선정 ETF 상세</h2>
      {build_table(selected_rows, [
        ("ticker", "티커"),
        ("etf_name", "ETF"),
        ("aum_krw_100m", "AUM(억원)"),
        ("cluster", "전략 클러스터"),
        ("same_exposure_group", "동일 노출 그룹"),
        ("target_weight", "비중"),
      ])}
      <div class="note">전체 188개 ETF master는 framework/etf-master.csv에 저장되어 있습니다.</div>
    </section>

    <section>
      <h2>주간 모니터링 현황</h2>
      {build_table(weekly_rows, [
        ("cluster", "전략 클러스터"),
        ("held_tickers", "보유 티커"),
        ("target_weight", "목표 비중"),
        ("momentum_status", "모멘텀 상태"),
        ("one_month_return", "1M"),
        ("three_month_return", "3M"),
        ("six_month_return", "6M"),
        ("above_20d_ma", "20D 상회"),
        ("above_60d_ma", "60D 상회"),
        ("drawdown_from_60d_high", "60D 고점 대비"),
        ("relative_rank", "상대순위"),
        ("cluster_score", "점수"),
        ("decision", "판정"),
        ("proposed_action", "필요 행동"),
        ("notes", "메모"),
      ])}
    </section>

    <section>
      <h2>리밸런싱 로그</h2>
      {build_table(rebalance_rows, [
        ("rebalance_date", "일자"),
        ("previous_total_risk", "기존 위험자산"),
        ("new_total_risk", "신규 위험자산"),
        ("turnover", "회전율"),
        ("trigger", "트리거"),
        ("result", "결과"),
      ])}
    </section>
  </main>
</body>
</html>
"""


def render_momentum_dashboard() -> str:
    equity = read_csv(FRAMEWORK_DIR / "equity-momentum.csv")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    price_data_as_of = equity[0].get("price_data_as_of", "미수집") if equity else "미수집"

    add_rows = [row for row in equity if row["decision"] == "Add"]
    cut_rows = [row for row in equity if row["decision"] == "Cut"]
    watch_rows = [row for row in equity if row["decision"] == "Watch"]
    hold_rows = [row for row in equity if row["decision"] == "Hold"]

    def row_view(row: dict[str, str]) -> dict[str, str]:
        return {
            "opportunity": row["opportunity"],
            "ticker": row["ticker"],
            "etf_name": row["etf_name"],
            "competition_category": row["competition_category"],
            "cluster": row["cluster"],
            "selected": "보유" if row.get("selected") == "Y" else "미보유",
            "target_weight": fmt_weight(row["target_weight"]),
            "one_month_return": row["one_month_return"],
            "three_month_return": row["three_month_return"],
            "six_month_return": row["six_month_return"],
            "above_20d_ma": row["above_20d_ma"],
            "above_60d_ma": row["above_60d_ma"],
            "drawdown_from_60d_high": row["drawdown_from_60d_high"],
            "relative_rank": row["relative_rank"],
            "momentum_score": row["momentum_score"],
            "decision": decision_label(row["decision"]),
            "decision_class": decision_class(row["decision"]),
        }

    ranked_rows = [row_view(row) for row in sorted(equity, key=lambda row: parse_score(row["momentum_score"]), reverse=True)]
    buy_rows = [row_view(row) for row in sorted(add_rows, key=lambda row: parse_score(row["momentum_score"]), reverse=True)[:12]]
    sell_rows = [row_view(row) for row in sorted(cut_rows, key=lambda row: parse_score(row["momentum_score"]))[:12]]

    best = ranked_rows[0] if ranked_rows else {}
    weakest = ranked_rows[-1] if ranked_rows else {}

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DB GAPS 주식 모멘텀 대시보드</title>
  <style>
{base_css(920)}
  </style>
</head>
<body>
  <header>
    <div class="hero">
      <div class="hero-copy">
        <h1>주식 모멘텀 대시보드</h1>
        <p>ETF 리스트에 포함된 전체 주식 ETF 유니버스의 모멘텀을 봅니다. 가격 데이터 기준일: {esc(price_data_as_of)}. 생성 시각: {esc(generated_at)}.</p>
      </div>
      <nav class="nav-pills" aria-label="dashboard navigation">
        <a href="index.html">종합</a>
        <a class="active" href="momentum.html">주식 모멘텀</a>
      </nav>
    </div>
  </header>
  <main>
    <section class="cards" aria-label="Momentum summary">
      <div class="card"><div class="label">확대 후보</div><div class="value">{len(add_rows)}</div></div>
      <div class="card"><div class="label">유지</div><div class="value">{len(hold_rows)}</div></div>
      <div class="card"><div class="label">관찰</div><div class="value">{len(watch_rows)}</div></div>
      <div class="card"><div class="label">축소 후보</div><div class="value">{len(cut_rows)}</div></div>
      <div class="card"><div class="label">전체 주식 ETF</div><div class="value">{len(equity)}</div></div>
    </section>

    <section class="grid-2">
      <div class="panel">
        <h2>가장 강한 모멘텀</h2>
        <p>{esc(best.get("ticker", "-"))} · {esc(best.get("etf_name", "-"))}</p>
        <p>점수 {esc(best.get("momentum_score", "-"))}, 3M {esc(best.get("three_month_return", "-"))}, 60D 고점 대비 {esc(best.get("drawdown_from_60d_high", "-"))}</p>
      </div>
      <div class="panel">
        <h2>가장 약한 모멘텀</h2>
        <p>{esc(weakest.get("ticker", "-"))} · {esc(weakest.get("etf_name", "-"))}</p>
        <p>점수 {esc(weakest.get("momentum_score", "-"))}, 3M {esc(weakest.get("three_month_return", "-"))}, 60D 고점 대비 {esc(weakest.get("drawdown_from_60d_high", "-"))}</p>
      </div>
    </section>

    <section class="guide">
      <div class="panel"><b>확대 후보</b>점수 80 이상. 카테고리 한도와 기존 비중을 확인한 뒤 증액 검토.</div>
      <div class="panel"><b>관찰 후보</b>점수 50-64. 다음 주 업데이트 전까지 신규 매수 보류.</div>
      <div class="panel"><b>축소 후보</b>점수 50 미만. 추세 이탈과 낙폭이 겹치면 교체 후보 탐색.</div>
    </section>

    <section class="grid-2">
      <div>
        <h2>매수/확대 후보 Top 12</h2>
        {build_table(buy_rows, [
          ("opportunity", "판정"),
          ("ticker", "티커"),
          ("etf_name", "ETF"),
          ("selected", "보유"),
          ("three_month_return", "3M"),
          ("above_60d_ma", "60D 상회"),
          ("momentum_score", "점수"),
        ])}
      </div>
      <div>
        <h2>매도/축소 후보 Top 12</h2>
        {build_table(sell_rows, [
          ("opportunity", "판정"),
          ("ticker", "티커"),
          ("etf_name", "ETF"),
          ("selected", "보유"),
          ("one_month_return", "1M"),
          ("drawdown_from_60d_high", "60D 고점 대비"),
          ("momentum_score", "점수"),
        ])}
      </div>
    </section>

    <section>
      <h2>주식 ETF 모멘텀 랭킹</h2>
      {build_table(ranked_rows, [
        ("opportunity", "판정"),
        ("ticker", "티커"),
        ("etf_name", "ETF"),
        ("competition_category", "분류"),
        ("cluster", "클러스터"),
        ("selected", "보유"),
        ("target_weight", "현재 비중"),
        ("one_month_return", "1M"),
        ("three_month_return", "3M"),
        ("six_month_return", "6M"),
        ("above_20d_ma", "20D"),
        ("above_60d_ma", "60D"),
        ("drawdown_from_60d_high", "60D 고점 대비"),
        ("relative_rank", "상대순위"),
        ("momentum_score", "점수"),
      ])}
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    PUBLIC_DIR.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(render_dashboard(), encoding="utf-8")
    MOMENTUM_OUTPUT_PATH.write_text(render_momentum_dashboard(), encoding="utf-8")
    print(f"wrote={OUTPUT_PATH}")
    print(f"wrote={MOMENTUM_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
