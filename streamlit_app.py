import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json, os

# ─────────────────────────────────────────────
# 1. 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="국가 에너지 및 산업 핵심지표 대시보드",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# 2. API 키
# ─────────────────────────────────────────────
KPX_SERVICE_KEY = "11d07546d5cc1d813529086db2074456e7567d7f15e13e2e4357e5f22a81495a"
ECOS_API_KEY    = "GFRDCL2A2MQA9HE04227"
KOSIS_API_KEY   = "MTEzNTViODg3YmVkYjM4MmNmNmJlNTAwMWQyMDBlZWM="
OPINET_API_KEY  = "ih5C0ZfGoxGs5GPXpW9aQv5cWB1nr8tdgZH7lN2Mk"

# ─────────────────────────────────────────────
# 3. CSS — 화이트 계열 테마
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700;900&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: #f4f6f9;
    color: #1a2332;
}

/* 헤더 */
.dash-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #1565c0 60%, #1976d2 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(21,101,192,0.25);
}
.dash-header::after {
    content: '';
    position: absolute;
    right: -60px; top: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.dash-title {
    font-size: 24px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin: 0;
}
.dash-title span { color: #90caf9; }
.dash-subtitle {
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    margin-top: 4px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* KPI 카드 */
.kpi-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px 18px;
    border-top: 4px solid;
    border-left: 1px solid #e8edf2;
    border-right: 1px solid #e8edf2;
    border-bottom: 1px solid #e8edf2;
    height: 130px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
}
.kpi-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.10);
    transform: translateY(-2px);
}
.kpi-name { font-size: 11px; color: #7b8fa6; font-weight: 600; letter-spacing: 0.04em; margin-bottom: 6px; }
.kpi-val  { font-size: 24px; font-weight: 900; color: #1a2332; line-height: 1; }
.kpi-unit { font-size: 12px; font-weight: 400; color: #9eaab8; margin-left: 3px; }
.kpi-sub  { font-size: 11px; font-weight: 600; margin-top: 4px; }
.kpi-date { font-size: 10px; color: #b0bec5; margin-top: 3px; letter-spacing: 0.02em; }

/* 섹션 타이틀 */
.section-title {
    font-size: 12px;
    font-weight: 700;
    color: #1565c0;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border-left: 3px solid #1565c0;
    padding-left: 10px;
    margin: 24px 0 14px 0;
}

/* 에러 박스 */
.error-box {
    background: #fff5f5;
    border-left: 5px solid #ef5350;
    border-radius: 8px;
    padding: 14px 20px;
    color: #c62828;
    font-size: 13px;
}

/* 푸터 */
.footer {
    font-size: 11px;
    color: #9eaab8;
    text-align: center;
    padding: 16px 0 8px;
    border-top: 1px solid #e8edf2;
    margin-top: 24px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 4. 데이터 수집 함수
# ─────────────────────────────────────────────

def get_realtime_pwr_detail():
    """KPX: JSON 파일 우선, 없으면 API 직접 호출"""
    json_path = os.path.join(os.path.dirname(__file__), "data", "kpx_latest.json")

    if os.path.exists(json_path):
        try:
            with open(json_path, encoding="utf-8") as f:
                payload = json.load(f)
            data = payload.get("records", [])
            if data:
                st.session_state['kpx_fetched_at'] = payload.get("fetched_at", "-")
                st.session_state['kpx_error'] = None
                return data
        except Exception as e:
            st.session_state['kpx_error'] = f"JSON 읽기 오류: {e}"

    try:
        url = 'https://openapi.kpx.or.kr/openapi/sukub5mToday/getSukub5mToday'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/xml, text/xml, */*",
            "Accept-Language": "ko-KR,ko;q=0.9",
            "Referer": "https://openapi.kpx.or.kr/",
        }
        res = requests.get(url, params={'serviceKey': KPX_SERVICE_KEY}, headers=headers, timeout=15)
        root = ET.fromstring(res.content)
        items = root.findall(".//item")
        if not items:
            raise ValueError("KPX 데이터 없음")
        data = []
        for item in items[-12:]:
            raw = item.findtext('baseDatetime')
            ft  = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]} {raw[8:10]}:{raw[10:12]}:{raw[12:14]}"
            data.append({
                "baseDatetime":   raw,
                "formatted_time": ft,
                "supp":  float(item.findtext('suppAbility')    or 0),
                "curr":  float(item.findtext('currPwrTot')     or 0),
                "spare": float(item.findtext('suppReservePwr') or 0),
                "ratio": item.findtext('suppReserveRate')      or "-",
            })
        st.session_state['kpx_fetched_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['kpx_error'] = None
        return data
    except Exception as e:
        st.session_state['kpx_error'] = str(e)
        if st.session_state.get('kpx_last_data'):
            return st.session_state['kpx_last_data']
        raise e


@st.cache_data(ttl=3600)
def get_strategic_data():
    items = []
    items.append({"name": "🌿 온실가스 배출량", "value": 624.2, "unit": "백만 톤",
                  "color": "#2e7d32", "sub": "🔻 전년比 4.4% 감소", "date": "2023년 확정치"})
    try:
        url = (f"https://kosis.kr/openapi/Param/statisticsParameterData.do"
               f"?method=getList&apiKey={KOSIS_API_KEY}&itmId=13103136288999+"
               f"&objL1=13102136288ACC_ITEM.20101+&format=json&jsonVD=Y"
               f"&prdSe=Y&newEstPrdCnt=1&orgId=301&tblId=DT_200Y10")
        res = requests.get(url, timeout=5).json()
        items.append({"name": "💰 GDP 성장률", "value": float(res[0]['DT']), "unit": "%",
                      "color": "#1565c0", "sub": "실질성장률", "date": "KOSIS 최신"})
    except:
        pass
    try:
        url = (f"http://ecos.bok.or.kr/api/StatisticSearch/{ECOS_API_KEY}"
               f"/json/kr/1/1/731Y001/D/20260306/20260306/0000001")
        res = requests.get(url, timeout=5).json()
        val = float(res['StatisticSearch']['row'][0]['DATA_VALUE'])
        items.append({"name": "💵 원/달러 환율", "value": val, "unit": "원",
                      "color": "#ef6c00", "sub": "시장평균", "date": datetime.now().strftime("%Y-%m-%d")})
    except:
        pass
    try:
        root = ET.fromstring(
            requests.get(f'https://www.opinet.co.kr/api/avgAllPrice.do?out=xml&certkey={OPINET_API_KEY}', timeout=5).content
        )
        for oil in root.findall('OIL'):
            if oil.findtext('PRODCD') == 'B027':
                items.append({"name": "⛽ 무연휘발유", "value": float(oil.findtext('PRICE')), "unit": "원/L",
                               "color": "#f9a825", "sub": "전국평균", "date": datetime.now().strftime("%Y-%m-%d")})
    except:
        pass
    return items


@st.cache_data(ttl=3600)
def get_kospi():
    """FinanceDataReader로 코스피 지수 조회"""
    try:
        import FinanceDataReader as fdr
        df = fdr.DataReader('KS11')
        if df.empty:
            return None
        latest = df.iloc[-1]
        prev   = df.iloc[-2]
        close  = float(latest['Close'])
        change = close - float(prev['Close'])
        chg_pct = change / float(prev['Close']) * 100
        return {
            "close":   close,
            "change":  change,
            "chg_pct": chg_pct,
            "date":    df.index[-1].strftime("%Y-%m-%d"),
            "open":    float(latest['Open']),
            "high":    float(latest['High']),
            "low":     float(latest['Low']),
            "volume":  float(latest.get('Volume', 0)),
        }
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 5. 헤더
# ─────────────────────────────────────────────
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div class="dash-header">
    <div class="dash-title">⚡ 국가 <span>에너지 및 산업</span> 핵심지표 대시보드</div>
    <div class="dash-subtitle">Energy Strategy &amp; Policy Planning Dashboard &nbsp;·&nbsp; v4.0 &nbsp;·&nbsp; 조회: {now_str}</div>
</div>
""", unsafe_allow_html=True)

col_r, col_info = st.columns([1, 6])
with col_r:
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_info:
    st.markdown(
        "<div style='padding-top:8px; font-size:12px; color:#9eaab8;'>"
        "⏱ KPX 15분 · KOSPI/ECOS/KOSIS/Opinet 1시간 간격 자동 갱신</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ─────────────────────────────────────────────
# 6. KPX 데이터 로드
# ─────────────────────────────────────────────
if 'kpx_error' not in st.session_state:
    st.session_state['kpx_error'] = None

try:
    pwr_list = get_realtime_pwr_detail()
    pwr = pwr_list[-1]
    supply_pct = round(pwr['curr'] / pwr['supp'] * 100, 1) if pwr['supp'] else 0
    if st.session_state.get('kpx_error'):
        st.warning(f"⚠️ KPX 연결 실패 — 캐시 데이터 표시 중  |  오류: {st.session_state['kpx_error']}")
except Exception as e:
    st.markdown(f"<div class='error-box'>⚠️ 전력 데이터 오류: {e}</div>", unsafe_allow_html=True)
    pwr_list, pwr, supply_pct = [], None, 0

# ─────────────────────────────────────────────
# 7. 핵심 전략 지표 (R&D + 거시 + KOSPI)
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>핵심 전략 지표</div>", unsafe_allow_html=True)

eco_items = get_strategic_data()
kospi_data = get_kospi()

# KOSPI 카드 데이터 준비
if kospi_data and "error" not in kospi_data:
    kospi_chg     = kospi_data['change']
    kospi_chg_pct = kospi_data['chg_pct']
    kospi_color   = "#c62828" if kospi_chg >= 0 else "#1565c0"
    kospi_arrow   = "▲" if kospi_chg >= 0 else "▼"
    kospi_sub     = f"{kospi_arrow} {abs(kospi_chg):,.2f} ({abs(kospi_chg_pct):.2f}%)"
    kospi_val     = f"{kospi_data['close']:,.2f}"
    kospi_date    = kospi_data['date']
else:
    kospi_color, kospi_sub, kospi_val, kospi_date = "#9eaab8", "데이터 없음", "-", "-"

kpi_cols = st.columns(6)

# R&D 예산
with kpi_cols[0]:
    st.markdown("""
    <div class="kpi-card" style="border-top-color:#e91e63;">
        <div class="kpi-name">🚀 '26년 정부 R&D 예산</div>
        <div class="kpi-val">35.3<span class="kpi-unit">조원</span></div>
        <div class="kpi-sub" style="color:#e91e63;">▲ 전년比 19.3% 증가</div>
        <div class="kpi-date">📅 2026년 정부 예산안</div>
    </div>
    """, unsafe_allow_html=True)

# 거시 지표 (온실가스, GDP, 환율, 유가)
for i, col in enumerate(kpi_cols[1:5]):
    if i < len(eco_items):
        item = eco_items[i]
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{item['color']};">
                <div class="kpi-name">{item['name']}</div>
                <div class="kpi-val">{item['value']:,.1f}<span class="kpi-unit">{item['unit']}</span></div>
                <div class="kpi-sub" style="color:{item['color']};">{item['sub']}</div>
                <div class="kpi-date">📅 {item.get('date', '-')}</div>
            </div>
            """, unsafe_allow_html=True)

# KOSPI
with kpi_cols[5]:
    st.markdown(f"""
    <div class="kpi-card" style="border-top-color:{kospi_color};">
        <div class="kpi-name">📈 KOSPI 지수</div>
        <div class="kpi-val" style="font-size:22px;">{kospi_val}<span class="kpi-unit">pt</span></div>
        <div class="kpi-sub" style="color:{kospi_color};">{kospi_sub}</div>
        <div class="kpi-date">📅 {kospi_date}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 8. 신재생에너지 설비 현황
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>신재생에너지 설비 현황</div>", unsafe_allow_html=True)

re_kpi_cols = st.columns(5)
re_cards = [
    {"name": "🌱 신재생에너지 총계", "value": "39,465.1", "unit": "MW", "color": "#00897b", "sub": "설비용량 합계", "date": "2025-12 기준"},
    {"name": "☀️ 태양광",           "value": "30,760.3", "unit": "MW", "color": "#f9a825", "sub": "전체의 77.9%",  "date": "2025-12 기준"},
    {"name": "💨 풍력",              "value": "2,437.3",  "unit": "MW", "color": "#29b6f6", "sub": "전체의 6.2%",   "date": "2025-12 기준"},
    {"name": "🌿 바이오",            "value": "2,561.4",  "unit": "MW", "color": "#43a047", "sub": "전체의 6.5%",   "date": "2025-12 기준"},
    {"name": "🔋 연료전지",          "value": "1,289.8",  "unit": "MW", "color": "#7b1fa2", "sub": "전체의 3.3%",   "date": "2025-12 기준"},
]
for i, col in enumerate(re_kpi_cols):
    card = re_cards[i]
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-top-color:{card['color']};">
            <div class="kpi-name">{card['name']}</div>
            <div class="kpi-val" style="font-size:22px;">{card['value']}<span class="kpi-unit">{card['unit']}</span></div>
            <div class="kpi-sub" style="color:{card['color']};">{card['sub']}</div>
            <div class="kpi-date">📅 {card['date']}</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 9. 실시간 전력 수급 현황
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>실시간 전력 수급 현황</div>", unsafe_allow_html=True)

pwr_cols = st.columns(3)
pwr_cards = [
    {"name": "🏭 발전설비용량", "value": "158,147", "unit": "MW",
     "color": "#1565c0", "sub": "원자력 26,050 · 석탄 40,766 · 가스 45,705 · 신재생 39,790",
     "date": "2026-03 기준"},
    {"name": "⚡ 현재 전력 수요", "value": f"{pwr['curr']:,.0f}" if pwr else "-", "unit": "MW",
     "color": "#e53935", "sub": "● LIVE", "date": pwr['formatted_time'] if pwr else "-"},
    {"name": "🔌 공급능력", "value": f"{pwr['supp']:,.0f}" if pwr else "-", "unit": "MW",
     "color": "#1976d2", "sub": "공급 가능량", "date": pwr['formatted_time'] if pwr else "-"},
]
for i, col in enumerate(pwr_cols):
    card = pwr_cards[i]
    with col:
        if i == 0:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{card['color']}; height:130px;">
                <div class="kpi-name">
                    <a href="https://epsis.kpx.or.kr/epsisnew/selectEkpoBftChart.do?menuId=020100"
                       target="_blank"
                       style="color:#7b8fa6; text-decoration:none;"
                       onmouseover="this.style.color='#1565c0';"
                       onmouseout="this.style.color='#7b8fa6';">
                        {card['name']} <span style="font-size:10px;">↗</span>
                    </a>
                </div>
                <div class="kpi-val">{card['value']}<span class="kpi-unit">{card['unit']}</span></div>
                <div style="font-size:10px; color:#9eaab8; margin-top:4px; line-height:1.6;">{card['sub']}</div>
                <div class="kpi-date">📅 {card['date']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{card['color']};">
                <div class="kpi-name">{card['name']}</div>
                <div class="kpi-val">{card['value']}<span class="kpi-unit">{card['unit']}</span></div>
                <div class="kpi-sub" style="color:{card['color']};">{card['sub']}</div>
                <div class="kpi-date">📅 {card['date']}</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 10. 푸터 + 자동 새로고침
# ─────────────────────────────────────────────
st.markdown(
    "<div class='footer'>"
    "데이터 출처: KPX(전력거래소) · FinanceDataReader(KOSPI) · ECOS(한국은행) · KOSIS(통계청) · Opinet(한국석유공사) · 정부 예산안<br>"
    "이 페이지는 15분마다 자동으로 새로고침됩니다."
    "</div>",
    unsafe_allow_html=True,
)

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=900_000, key="autorefresh")
except ImportError:
    pass
