"""
GitHub Actions에서 실행되는 데이터 수집 스크립트.
- KPX 전력 데이터  → data/kpx_latest.json
- KOSPI 지수       → data/kospi_latest.json
"""
import requests
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

SERVICE_KEY = "11d07546d5cc1d813529086db2074456e7567d7f15e13e2e4357e5f22a81495a"

# ─────────────────────────────────────────────
# 1. KPX 전력 데이터
# ─────────────────────────────────────────────
def fetch_kpx():
    url = "https://openapi.kpx.or.kr/openapi/sukub5mToday/getSukub5mToday"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/xml, text/xml, */*",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://openapi.kpx.or.kr/",
    }
    res = requests.get(url, params={"serviceKey": SERVICE_KEY}, headers=headers, timeout=15)
    root = ET.fromstring(res.content)
    items = root.findall(".//item")
    if not items:
        raise ValueError("KPX 데이터 없음")

    results = []
    for item in items[-12:]:
        raw = item.findtext("baseDatetime")
        ft  = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]} {raw[8:10]}:{raw[10:12]}:{raw[12:14]}"
        results.append({
            "baseDatetime":   raw,
            "formatted_time": ft,
            "supp":  float(item.findtext("suppAbility")    or 0),
            "curr":  float(item.findtext("currPwrTot")     or 0),
            "spare": float(item.findtext("suppReservePwr") or 0),
            "ratio": item.findtext("suppReserveRate")      or "-",
        })
    return results


# ─────────────────────────────────────────────
# 2. KOSPI 지수 — yfinance
# ─────────────────────────────────────────────
def fetch_kospi():
    import yfinance as yf
    df = yf.download("^KS11", period="5d", progress=False, auto_adjust=True)
    df = df.dropna(subset=["Close"])
    if len(df) < 2:
        raise ValueError("KOSPI 데이터 부족")

    # MultiIndex 컬럼 처리 (yfinance 0.2+)
    if hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)

    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    close   = float(latest["Close"])
    change  = close - float(prev["Close"])
    chg_pct = change / float(prev["Close"]) * 100

    return {
        "close":   round(close, 2),
        "change":  round(change, 2),
        "chg_pct": round(chg_pct, 2),
        "open":    round(float(latest["Open"]), 2),
        "high":    round(float(latest["High"]), 2),
        "low":     round(float(latest["Low"]), 2),
        "date":    df.index[-1].strftime("%Y-%m-%d"),
    }


# ─────────────────────────────────────────────
# 3. 메인
# ─────────────────────────────────────────────
def main():
    os.makedirs("data", exist_ok=True)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # KPX
    try:
        kpx_data = fetch_kpx()
        with open("data/kpx_latest.json", "w", encoding="utf-8") as f:
            json.dump({"fetched_at": now, "records": kpx_data}, f, ensure_ascii=False, indent=2)
        print(f"✅ KPX 저장 완료: {len(kpx_data)}건")
    except Exception as e:
        print(f"❌ KPX 오류: {e}")

    # KOSPI
    try:
        kospi_data = fetch_kospi()
        with open("data/kospi_latest.json", "w", encoding="utf-8") as f:
            json.dump({"fetched_at": now, **kospi_data}, f, ensure_ascii=False, indent=2)
        print(f"✅ KOSPI 저장 완료: {kospi_data['close']} ({kospi_data['date']})")
    except Exception as e:
        print(f"❌ KOSPI 오류: {e}")
        with open("data/kospi_latest.json", "w", encoding="utf-8") as f:
            json.dump({"fetched_at": now, "error": str(e)}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
