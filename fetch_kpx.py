"""
GitHub Actions에서 실행되는 KPX 데이터 수집 스크립트.
수집한 데이터를 data/kpx_latest.json 에 저장합니다.
"""
import requests
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

SERVICE_KEY = "11d07546d5cc1d813529086db2074456e7567d7f15e13e2e4357e5f22a81495a"
OUTPUT_PATH = "data/kpx_latest.json"

def fetch():
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

def main():
    os.makedirs("data", exist_ok=True)
    try:
        data = fetch()
        payload = {
            "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "records": data,
        }
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"✅ 저장 완료: {len(data)}건 → {OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ 오류: {e}")
        raise

if __name__ == "__main__":
    main()
