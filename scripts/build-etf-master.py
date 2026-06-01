#!/usr/bin/env python3
"""Build the enriched ETF master for the DB GAPS EMP framework."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "framework" / "initial-portfolio.csv"
OUTPUT_PATH = ROOT / "framework" / "etf-master.csv"


CATEGORY_LIMITS = {
    "국내주식_지수": 30,
    "국내주식_섹터": 15,
    "해외주식_지수": 30,
    "해외주식_섹터": 10,
    "FX 및 원자재": 20,
    "국내채권_종합": 50,
    "국내채권_회사채": 30,
    "해외채권_종합": 50,
    "해외채권_회사채": 30,
    "금리연계형/초단기채권": 50,
}


def clean_number(value: str) -> int:
    return int(value.replace(",", "").strip() or "0")


def find_universe_path() -> Path:
    matches = sorted(ROOT.glob("*GAPS_ETF*ETF.csv"))
    if not matches:
        raise FileNotFoundError("Could not find competition ETF universe CSV matching '*GAPS_ETF*ETF.csv'")
    return matches[0]


def normalize_bucket(risk_label: str) -> str:
    return "Risk" if risk_label == "위험" else "Safe"


def classify_cluster(name: str, index_name: str, category: str) -> str:
    text = f"{name} {index_name}"

    if any(keyword in text for keyword in ["AI반도체", "필라델피아AI반도체", "미국반도체", "글로벌반도체", "K-반도체"]):
        return "AI & Semiconductors"
    if "반도체" in text:
        return "AI & Semiconductors"
    if any(keyword in text for keyword in ["AI전력", "전력핵심", "원자력", "유틸리티"]):
        return "AI Power Infrastructure"
    if any(keyword in text for keyword in ["조선", "방산", "우주", "중공업", "산업재"]):
        return "Korea Cyclical Alpha"
    if any(keyword in text for keyword in ["S&P500", "나스닥100", "KODEX 200", "TIGER 200", "MSCI Korea", "코스피", "코스닥150"]):
        return "Core Equity Beta"
    if any(keyword in text for keyword in ["금", "골드", "WTI", "원유", "은선물", "농산물", "달러선물", "엔선물"]):
        return "Commodity Hedge"
    if any(keyword in text for keyword in ["CD금리", "KOFR", "머니마켓", "초단기", "단기채권", "단기통안채"]):
        return "Short-Duration Safety"
    if any(keyword in text for keyword in ["종합채권", "회사채", "국고채", "국채", "통안채", "금융채", "은행채"]):
        if "미국" in text or "일본" in text:
            return "USD Safety" if "단기" in text or "달러" in text else "Global Bonds"
        return "Domestic Carry"
    if "미국달러단기채권" in text:
        return "USD Safety"
    if category.startswith("해외채권"):
        return "Global Bonds"
    if category.startswith("국내채권"):
        return "Domestic Carry"
    if category == "금리연계형/초단기채권":
        return "Short-Duration Safety"
    if category in {"해외주식_지수", "국내주식_지수"}:
        return "Core Equity Beta"
    if category in {"해외주식_섹터", "국내주식_섹터"}:
        return "Satellite Equity"
    return "Reserve"


def same_exposure_group(name: str, index_name: str, category: str, cluster: str) -> str:
    text = f"{name} {index_name}"
    brandless = (
        text.replace("KODEX", "")
        .replace("TIGER", "")
        .replace("ACE", "")
        .replace("RISE", "")
        .replace("PLUS", "")
        .replace("SOL", "")
        .replace("KIWOOM", "")
        .replace("HANARO", "")
        .replace("WON", "")
        .replace("TIME", "")
        .strip()
    )

    if "S&P500" in text:
        return "US S&P500"
    if "나스닥100" in text:
        return "US Nasdaq100"
    if "코스닥150" in text:
        return "Korea KOSDAQ150"
    if "KODEX 200" in text or "TIGER 200" in text or "200TR" in text or "코스피200" in text:
        return "Korea KOSPI200"
    if "반도체" in text:
        return "Semiconductors"
    if "AI전력" in text or "전력핵심" in text:
        return "AI Power"
    if "조선" in text:
        return "Korea Shipbuilding"
    if "방산" in text or "우주" in text:
        return "Korea Defense"
    if "금" in text or "골드" in text:
        return "Gold"
    if "WTI" in text or "원유" in text:
        return "WTI Oil"
    if "CD금리" in text:
        return "CD Rate"
    if "KOFR" in text:
        return "KOFR"
    if "머니마켓" in text:
        return "Money Market"
    return f"{cluster}: {brandless or category}"


def load_portfolio() -> dict[str, dict[str, str]]:
    with PORTFOLIO_PATH.open(newline="", encoding="utf-8") as handle:
        return {row["ticker"]: row for row in csv.DictReader(handle)}


def load_universe() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    universe_path = find_universe_path()
    with universe_path.open(newline="", encoding="utf-8-sig") as handle:
        for raw in csv.reader(handle):
            if len(raw) <= 6 or not raw[1].strip().startswith("A"):
                continue
            ticker = raw[1].strip()
            name = raw[2].strip()
            aum = clean_number(raw[3])
            index_name = raw[4].strip()
            risk_label = raw[5].strip()
            category = raw[6].strip()
            cluster = classify_cluster(name, index_name, category)
            rows.append(
                {
                    "ticker": ticker,
                    "etf_name": name,
                    "aum_krw_100m": str(aum),
                    "index_name": index_name,
                    "asset_bucket": normalize_bucket(risk_label),
                    "risk_label": risk_label,
                    "competition_category": category,
                    "category_limit": str(CATEGORY_LIMITS.get(category, "")),
                    "cluster": cluster,
                    "same_exposure_group": same_exposure_group(name, index_name, category, cluster),
                }
            )
    return rows


def main() -> None:
    portfolio = load_portfolio()
    rows = load_universe()

    for row in rows:
        selected = portfolio.get(row["ticker"])
        if selected:
            row["cluster"] = selected["cluster"]
        row["selected"] = "Y" if selected else "N"
        row["target_weight"] = selected["target_weight"] if selected else "0"
        row["selected_role"] = selected["role"] if selected else ""
        row["thesis"] = selected["thesis"] if selected else ""
        row["action_trigger"] = selected["action_trigger"] if selected else ""

    fields = [
        "ticker",
        "etf_name",
        "aum_krw_100m",
        "index_name",
        "asset_bucket",
        "risk_label",
        "competition_category",
        "category_limit",
        "cluster",
        "same_exposure_group",
        "selected",
        "target_weight",
        "selected_role",
        "thesis",
        "action_trigger",
    ]

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    selected_count = sum(1 for row in rows if row["selected"] == "Y")
    total_weight = sum(float(row["target_weight"]) for row in rows)
    print(f"wrote={OUTPUT_PATH}")
    print(f"rows={len(rows)} selected={selected_count} total_weight={total_weight:g}")


if __name__ == "__main__":
    main()
