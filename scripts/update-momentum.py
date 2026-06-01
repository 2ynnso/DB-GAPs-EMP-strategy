#!/usr/bin/env python3
"""Fetch ETF prices and update the weekly monitoring dashboard."""

from __future__ import annotations

import csv
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_DIR = ROOT / "framework"
PORTFOLIO_PATH = FRAMEWORK_DIR / "initial-portfolio.csv"
ETF_MASTER_PATH = FRAMEWORK_DIR / "etf-master.csv"
WEEKLY_PATH = FRAMEWORK_DIR / "weekly-monitoring-dashboard.csv"
EQUITY_MOMENTUM_PATH = FRAMEWORK_DIR / "equity-momentum.csv"

TRADING_DAYS_1M = 21
TRADING_DAYS_3M = 63
TRADING_DAYS_6M = 126

REQUIRED_FIELDS = [
    "week_start",
    "cluster",
    "held_tickers",
    "target_weight",
    "current_weight",
    "one_month_return",
    "three_month_return",
    "six_month_return",
    "above_20d_ma",
    "above_60d_ma",
    "drawdown_from_60d_high",
    "relative_rank",
    "flow_signal",
    "macro_signal",
    "cluster_score",
    "decision",
    "proposed_action",
    "notes",
    "price_data_as_of",
    "data_source",
]

EQUITY_MOMENTUM_FIELDS = [
    "price_data_as_of",
    "ticker",
    "etf_name",
    "competition_category",
    "cluster",
    "target_weight",
    "selected",
    "one_month_return",
    "three_month_return",
    "six_month_return",
    "above_20d_ma",
    "above_60d_ma",
    "drawdown_from_60d_high",
    "relative_rank",
    "momentum_score",
    "decision",
    "opportunity",
    "data_source",
]

EQUITY_CATEGORIES = {
    "국내주식_지수",
    "국내주식_섹터",
    "해외주식_지수",
    "해외주식_섹터",
}

DEFENSIVE_CLUSTERS = {
    "Short-Duration Safety",
    "Domestic Carry",
    "USD Safety",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def ticker_to_yahoo_symbol(ticker: str) -> str:
    code = ticker.strip()
    if code.startswith("A"):
        code = code[1:]
    return f"{code}.KS"


def fetch_chart(symbol: str, retries: int = 3) -> list[tuple[int, float]]:
    params = urllib.parse.urlencode(
        {
            "range": "8mo",
            "interval": "1d",
            "includePrePost": "false",
            "events": "history",
        }
    )
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?{params}"
    headers = {
        "User-Agent": "Mozilla/5.0 DB-GAPS-EMP-dashboard/1.0",
        "Accept": "application/json",
    }
    request = urllib.request.Request(url, headers=headers)

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            result = payload["chart"]["result"][0]
            timestamps = result.get("timestamp") or []
            quote = result["indicators"]["quote"][0]
            closes = quote.get("close") or []
            points = [
                (int(ts), float(close))
                for ts, close in zip(timestamps, closes)
                if close is not None and math.isfinite(float(close))
            ]
            if len(points) < TRADING_DAYS_3M:
                raise ValueError(f"{symbol} returned only {len(points)} valid closes")
            return points
        except Exception as exc:  # noqa: BLE001 - surface final API failure with context
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed to fetch Yahoo chart data for {symbol}: {last_error}")


def pct_return(closes: list[float], lookback: int) -> float:
    if len(closes) <= lookback:
        lookback = len(closes) - 1
    if lookback <= 0 or closes[-lookback - 1] == 0:
        return 0.0
    return (closes[-1] / closes[-lookback - 1] - 1) * 100


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def weighted_average(items: list[tuple[float, float]]) -> float:
    total_weight = sum(weight for weight, value in items)
    if total_weight == 0:
        return 0.0
    return sum(weight * value for weight, value in items) / total_weight


def format_pct(value: float) -> str:
    return f"{value:.2f}%"


def format_bool(value: bool) -> str:
    return "Y" if value else "N"


def decision_from_score(score: float, cluster: str) -> str:
    if cluster in DEFENSIVE_CLUSTERS:
        return "Hold" if score >= 35 else "Watch"
    if score >= 80:
        return "Add"
    if score >= 65:
        return "Hold"
    if score >= 50:
        return "Watch"
    return "Cut"


def action_from_decision(decision: str) -> str:
    return {
        "Add": "Positive momentum confirmed; review category limits before adding",
        "Hold": "Momentum acceptable; keep current allocation",
        "Watch": "Momentum mixed; review next weekly update before trading",
        "Cut": "Momentum weak; prepare reduction or replacement candidate",
    }[decision]


def build_price_metrics(rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, float | bool | str]], str]:
    metrics: dict[str, dict[str, float | bool | str]] = {}
    latest_timestamps: list[int] = []

    for row in rows:
        ticker = row["ticker"]
        if ticker in metrics:
            continue
        symbol = ticker_to_yahoo_symbol(ticker)
        try:
            points = fetch_chart(symbol)
        except Exception as exc:  # noqa: BLE001 - keep the full universe visible even if one ETF fails
            metrics[ticker] = {
                "symbol": symbol,
                "error": str(exc),
            }
            continue
        timestamps = [ts for ts, close in points]
        closes = [close for ts, close in points]
        latest_timestamps.append(timestamps[-1])

        ma20 = average(closes[-20:])
        ma60 = average(closes[-60:])
        high60 = max(closes[-60:])
        drawdown = (closes[-1] / high60 - 1) * 100 if high60 else 0.0

        metrics[ticker] = {
            "symbol": symbol,
            "latest_close": closes[-1],
            "one_month_return": pct_return(closes, TRADING_DAYS_1M),
            "three_month_return": pct_return(closes, TRADING_DAYS_3M),
            "six_month_return": pct_return(closes, TRADING_DAYS_6M),
            "above_20d_ma": closes[-1] >= ma20,
            "above_60d_ma": closes[-1] >= ma60,
            "drawdown_from_60d_high": drawdown,
        }

    if not latest_timestamps:
        raise RuntimeError("no price data fetched")
    as_of_ts = max(latest_timestamps)
    as_of = datetime.fromtimestamp(as_of_ts, tz=timezone.utc).strftime("%Y-%m-%d")
    return metrics, as_of


def require_metric(ticker: str, metrics: dict[str, dict[str, float | bool | str]]) -> dict[str, float | bool | str]:
    metric = metrics.get(ticker)
    if not metric or "error" in metric:
        raise RuntimeError(f"required ticker {ticker} has no usable price data: {metric}")
    return metric


def cluster_metrics(
    weekly_row: dict[str, str],
    weights: dict[str, float],
    metrics: dict[str, dict[str, float | bool | str]],
) -> dict[str, float | bool]:
    tickers = [ticker.strip() for ticker in weekly_row["held_tickers"].split(";") if ticker.strip()]
    selected = [(weights.get(ticker, 0.0), require_metric(ticker, metrics)) for ticker in tickers if ticker in metrics]
    if not selected:
        raise ValueError(f"no fetched price metrics for cluster {weekly_row['cluster']}")

    def weighted_metric(key: str) -> float:
        return weighted_average([(weight, float(metric[key])) for weight, metric in selected])

    one_month = weighted_metric("one_month_return")
    three_month = weighted_metric("three_month_return")
    six_month = weighted_metric("six_month_return")
    drawdown = weighted_metric("drawdown_from_60d_high")
    trend20 = weighted_average([(weight, 100.0 if bool(metric["above_20d_ma"]) else 0.0) for weight, metric in selected]) >= 50
    trend60 = weighted_average([(weight, 100.0 if bool(metric["above_60d_ma"]) else 0.0) for weight, metric in selected]) >= 50

    return {
        "one_month_return": one_month,
        "three_month_return": three_month,
        "six_month_return": six_month,
        "above_20d_ma": trend20,
        "above_60d_ma": trend60,
        "drawdown_from_60d_high": drawdown,
    }


def score_cluster(row: dict[str, float | bool], relative_percentile: float) -> float:
    absolute_score = 0
    absolute_score += 20 if float(row["one_month_return"]) > 0 else 0
    absolute_score += 20 if float(row["three_month_return"]) > 0 else 0
    absolute_score += 15 if float(row["six_month_return"]) > 0 else 0
    absolute_score += 15 if bool(row["above_20d_ma"]) else 0
    absolute_score += 15 if bool(row["above_60d_ma"]) else 0

    drawdown = float(row["drawdown_from_60d_high"])
    if drawdown > -3:
        risk_score = 15
    elif drawdown > -8:
        risk_score = 8
    else:
        risk_score = 0

    return round(0.70 * (absolute_score + risk_score) + 0.30 * relative_percentile, 1)


def score_equity(metric: dict[str, float | bool | str], relative_percentile: float) -> float:
    row = {
        "one_month_return": metric["one_month_return"],
        "three_month_return": metric["three_month_return"],
        "six_month_return": metric["six_month_return"],
        "above_20d_ma": metric["above_20d_ma"],
        "above_60d_ma": metric["above_60d_ma"],
        "drawdown_from_60d_high": metric["drawdown_from_60d_high"],
    }
    return score_cluster(row, relative_percentile)


def opportunity_label(decision: str) -> str:
    return {
        "Add": "매수/확대 후보",
        "Hold": "보유 유지",
        "Watch": "관찰 후보",
        "Cut": "매도/축소 후보",
    }[decision]


def write_equity_momentum(
    equity_universe: list[dict[str, str]],
    metrics: dict[str, dict[str, float | bool | str]],
    as_of: str,
) -> None:
    equity_rows = [
        row for row in equity_universe
        if row["competition_category"] in EQUITY_CATEGORIES
    ]
    ranked = sorted(
        [row for row in equity_rows if row["ticker"] in metrics and "error" not in metrics[row["ticker"]]],
        key=lambda row: float(metrics[row["ticker"]]["three_month_return"]),
        reverse=True,
    )
    rank_lookup = {row["ticker"]: index + 1 for index, row in enumerate(ranked)}
    count = len(ranked)

    output: list[dict[str, str]] = []
    for row in equity_rows:
        ticker = row["ticker"]
        metric = metrics.get(ticker, {})
        if not metric or "error" in metric:
            output.append(
                {
                    "price_data_as_of": as_of,
                    "ticker": ticker,
                    "etf_name": row["etf_name"],
                    "competition_category": row["competition_category"],
                    "cluster": row["cluster"],
                    "target_weight": row.get("target_weight", "0"),
                    "selected": row.get("selected", "N"),
                    "one_month_return": "",
                    "three_month_return": "",
                    "six_month_return": "",
                    "above_20d_ma": "",
                    "above_60d_ma": "",
                    "drawdown_from_60d_high": "",
                    "relative_rank": "",
                    "momentum_score": "",
                    "decision": "Watch",
                    "opportunity": "데이터 확인 필요",
                    "data_source": f"Fetch failed: {metric.get('error', 'unknown error')}",
                }
            )
            continue

        rank = rank_lookup[ticker]
        relative_percentile = 100 if count == 1 else 100 * (count - rank) / (count - 1)
        score = score_equity(metric, relative_percentile)
        decision = decision_from_score(score, row["cluster"])
        output.append(
            {
                "price_data_as_of": as_of,
                "ticker": ticker,
                "etf_name": row["etf_name"],
                "competition_category": row["competition_category"],
                "cluster": row["cluster"],
                "target_weight": row.get("target_weight", "0"),
                "selected": row.get("selected", "N"),
                "one_month_return": format_pct(float(metric["one_month_return"])),
                "three_month_return": format_pct(float(metric["three_month_return"])),
                "six_month_return": format_pct(float(metric["six_month_return"])),
                "above_20d_ma": format_bool(bool(metric["above_20d_ma"])),
                "above_60d_ma": format_bool(bool(metric["above_60d_ma"])),
                "drawdown_from_60d_high": format_pct(float(metric["drawdown_from_60d_high"])),
                "relative_rank": f"{rank}/{count}",
                "momentum_score": f"{score:.1f}",
                "decision": decision,
                "opportunity": opportunity_label(decision),
                "data_source": "Yahoo Finance chart API",
            }
        )

    output.sort(key=lambda row: float(row["momentum_score"] or "-999"), reverse=True)
    with EQUITY_MOMENTUM_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EQUITY_MOMENTUM_FIELDS)
        writer.writeheader()
        writer.writerows(output)


def update_weekly_dashboard() -> None:
    portfolio = read_csv(PORTFOLIO_PATH)
    etf_master = read_csv(ETF_MASTER_PATH)
    weekly = read_csv(WEEKLY_PATH)
    weights = {row["ticker"]: float(row["target_weight"]) for row in portfolio}
    equity_universe = [row for row in etf_master if row["competition_category"] in EQUITY_CATEGORIES]
    fetch_rows = list({row["ticker"]: row for row in [*portfolio, *equity_universe]}.values())
    metrics, as_of = build_price_metrics(fetch_rows)
    write_equity_momentum(equity_universe, metrics, as_of)

    computed = {
        row["cluster"]: cluster_metrics(row, weights, metrics)
        for row in weekly
    }
    ranked = sorted(
        computed.items(),
        key=lambda item: float(item[1]["three_month_return"]),
        reverse=True,
    )
    rank_lookup = {
        cluster: index + 1
        for index, (cluster, values) in enumerate(ranked)
    }
    count = len(ranked)

    updated: list[dict[str, str]] = []
    for row in weekly:
        cluster = row["cluster"]
        values = computed[cluster]
        rank = rank_lookup[cluster]
        relative_percentile = 100 if count == 1 else 100 * (count - rank) / (count - 1)
        score = score_cluster(values, relative_percentile)
        decision = decision_from_score(score, cluster)

        next_row = {field: row.get(field, "") for field in REQUIRED_FIELDS}
        next_row["current_weight"] = row["target_weight"]
        next_row["one_month_return"] = format_pct(float(values["one_month_return"]))
        next_row["three_month_return"] = format_pct(float(values["three_month_return"]))
        next_row["six_month_return"] = format_pct(float(values["six_month_return"]))
        next_row["above_20d_ma"] = format_bool(bool(values["above_20d_ma"]))
        next_row["above_60d_ma"] = format_bool(bool(values["above_60d_ma"]))
        next_row["drawdown_from_60d_high"] = format_pct(float(values["drawdown_from_60d_high"]))
        next_row["relative_rank"] = f"{rank}/{count}"
        next_row["flow_signal"] = row.get("flow_signal") or "Manual check"
        next_row["macro_signal"] = row.get("macro_signal") or "Manual check"
        next_row["cluster_score"] = f"{score:.1f}"
        next_row["decision"] = decision
        next_row["proposed_action"] = action_from_decision(decision)
        next_row["notes"] = f"Auto-updated from Yahoo Finance chart API as of {as_of}"
        next_row["price_data_as_of"] = as_of
        next_row["data_source"] = "Yahoo Finance chart API"
        updated.append(next_row)

    with WEEKLY_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerows(updated)

    print(f"updated={WEEKLY_PATH}")
    print(f"updated={EQUITY_MOMENTUM_PATH}")
    print(f"clusters={len(updated)} price_data_as_of={as_of}")


if __name__ == "__main__":
    update_weekly_dashboard()
