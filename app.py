import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

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
KPX_SERVICE_KEY  = "11d07546d5cc1d813529086db2074456e7567d7f15e13e2e4357e5f22a81495a"
ECOS_API_KEY     = "GFRDCL2A2MQA9HE04227"
KOSIS_API_KEY    = "MTEzNTViODg3YmVkYjM4MmNmNmJlNTAwMWQyMDBlZWM="
OPINET_API_KEY   = "ih5C0ZfGoxGs5GPXpW9aQv5cWB1nr8tdgZH7lN2Mk"

# ─────────────────────────────────────────────
# 3. CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700;900&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

.dash-header {
    background: linear-gradient(135deg, #0a1628 0%, #0d2240 60%, #0f2a50 100%);
    border-bottom: 1px solid rgba(66,165,245,0.25);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.dash-header::after {
    content: '';
    position: absolute;
    right: -80px; top: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,180,255,0.07) 0%, transparent 70%);
    border-radius: 50%;
}
.dash-title {
    font-size: 26px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin: 0;
}
.dash-title span { color: #42a5f5; }
.dash-subtitle {
    font-size: 12px;
    color: #90a4ae;
    margin-top: 4px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.pwr-bar {
    background: linear-gradient(90deg, #060e1a, #0a1628, #060e1a);
    border: 1px solid rgba(66,165,245,0.2);
    border-radius: 12px;
    padding: 16px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    box-shadow: 0 0 30px rgba(0,100,200,0.15);
}
.pwr-item { text-align: center; flex: 1; }
.pwr-label { font-size: 10px; color: #546e7a; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px; }
.pwr-value { font-family: 'Share Tech Mono', monospace; font-size: 20px; font-weight: 700; }
.pwr-divider { width: 1px; height: 40px; background: rgba(255,255,255,0.08); flex-shrink: 0; }
.pwr-time { font-size: 10px; color: #546e7a; text-align: right; padding-left: 20px; border-left: 1px solid rgba(255,255,255,0.08); white-space: nowrap; }

.kpi-card {
    background: #0d1b2a;
    border-radius: 14px;
    padding: 18px 20px;
    border-top: 4px solid;
    border-left: 1px solid rgba(255,255,255,0.05);
    border-right: 1px solid rgba(255,255,255,0.05);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    height: 130px;
    position: relative;
    overflow: hidden;
}
.kpi-name { font-size: 11px; color: #78909c; font-weight: 600; letter-spacing: 0.04em; margin-bottom: 8px; }
.kpi-val { font-size: 26px; font-weight: 900; color: #fff; line-height: 1; }
.kpi-unit { font-size: 13px; font-weight: 400; color: #90a4ae; margin-left: 3px; }
.kpi-sub { font-size: 11px; font-weight: 600; margin-top: 4px; }
.kpi-date { font-size: 10px; color: #455a64; margin-top: 3px; letter-spacing: 0.02em; }

.section-title {
    font-size: 12px;
    font-weight: 700;
    color: #42a5f5;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border-left: 3px solid #42a5f5;
    padding-left: 10px;
    margin: 24px 0 14px 0;
}

.pwr-detail-card {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a3a5c 60%, #1565c0 100%);
    border-radius: 16px;
    padding: 28px 32px;
    border-left: 5px solid #42a5f5;
    box-shadow: 0 8px 32px rgba(21,101,192,0.25);
    position: relative;
    overflow: hidden;
    height: 100%;
}
.pwr-detail-card::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(66,165,245,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.live-badge {
    display: inline-block;
    background: #1b5e20;
    color: #a5d6a7;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid #388e3c;
    margin-bottom: 12px;
    letter-spacing: 0.05em;
}
.big-power {
    font-family: 'Share Tech Mono', monospace;
    font-size: 52px;
    font-weight: 900;
    color: #fff;
    line-height: 1;
    text-shadow: 0 0 24px rgba(66,165,245,0.5);
}
.big-unit { font-size: 20px; color: #90caf9; font-weight: 400; margin-left: 6px; }
.ts-box {
    display: inline-block;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    color: #b0bec5;
    margin-top: 18px;
}

.error-box {
    background: #1a0a0a;
    border-left: 5px solid #ef5350;
    border-radius: 8px;
    padding: 14px 20px;
    color: #ef9a9a;
    font-size: 13px;
}

.footer {
    font-size: 11px;
    color: #546e7a;
    text-align: center;
    padding: 16px 0 8px;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin-top: 24px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 4. 데이터 수집 함수
# ─────────────────────────────────────────────

def _fetch_kpx_raw():
    """KPX API 실제 호출 — 프록시 우회 헤더 포함"""
    url = 'https://openapi.kpx.or.kr/openapi/sukub5mToday/getSukub5mToday'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/xml, text/xml, */*",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://openapi.kpx.or.kr/",
    }
    res = requests.get(
        url,
        params={'serviceKey': KPX_SERVICE_KEY},
        headers=headers,
        timeout=15,
        verify=True,
    )
    root = ET.fromstring(res.content)
    items = root.findall(".//item")
    if not items:
        raise ValueError("KPX 데이터 없음")
    results = []
    for item in items[-12:]:
        raw_time = item.findtext('baseDatetime')
        ft = f"{raw_time[:4]}-{raw_time[4:6]}-{raw_time[6:8]} {raw_time[8:10]}:{raw_time[10:12]}:{raw_time[12:14]}"
        results.append({
            "baseDatetime":   raw_time,
            "formatted_time": ft,
            "supp":  float(item.findtext('suppAbility') or 0),
            "curr":  float(item.findtext('currPwrTot') or 0),
            "spare": float(item.findtext('suppReservePwr') or 0),
            "ratio": item.findtext('suppReserveRate') or "-",
        })
    return results


def get_realtime_pwr_detail():
    """KPX 데이터 조회 — 실패 시 마지막 성공 데이터 반환"""
    try:
        data = _fetch_kpx_raw()
        st.session_state['kpx_last_data'] = data
        st.session_state['kpx_last_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['kpx_error'] = None
        return data
    except Exception as e:
        st.session_state['kpx_error'] = str(e)
        if 'kpx_last_data' in st.session_state and st.session_state['kpx_last_data']:
            return st.session_state['kpx_last_data']
        raise e


@st.cache_data(ttl=3600)
def get_strategic_data():
    items = []
    items.append({"name": "🌿 온실가스 배출량", "value": 624.2, "unit": "백만 톤", "color": "#2e7d32", "sub": "🔻 전년比 4.4% 감소", "date": "2023년 확정치"})

    try:
        url = (f"https://kosis.kr/openapi/Param/statisticsParameterData.do"
               f"?method=getList&apiKey={KOSIS_API_KEY}&itmId=13103136288999+"
               f"&objL1=13102136288ACC_ITEM.20101+&format=json&jsonVD=Y"
               f"&prdSe=Y&newEstPrdCnt=1&orgId=301&tblId=DT_200Y10")
        res = requests.get(url, timeout=5).json()
        items.append({"name": "💰 GDP 성장률", "value": float(res[0]['DT']), "unit": "%", "color": "#1565c0", "sub": "실질성장률", "date": "KOSIS 최신"})
    except:
        pass

    try:
        url = (f"http://ecos.bok.or.kr/api/StatisticSearch/{ECOS_API_KEY}"
               f"/json/kr/1/1/731Y001/D/20260306/20260306/0000001")
        res = requests.get(url, timeout=5).json()
        val = float(res['StatisticSearch']['row'][0]['DATA_VALUE'])
        items.append({"name": "💵 원/달러 환율", "value": val, "unit": "원", "color": "#ef6c00", "sub": "시장평균", "date": datetime.now().strftime("%Y-%m-%d")})
    except:
        pass

    try:
        root = ET.fromstring(
            requests.get(
                f'https://www.opinet.co.kr/api/avgAllPrice.do?out=xml&certkey={OPINET_API_KEY}',
                timeout=5
            ).content
        )
        for oil in root.findall('OIL'):
            if oil.findtext('PRODCD') == 'B027':
                items.append({"name": "⛽ 무연휘발유", "value": float(oil.findtext('PRICE')), "unit": "원/L", "color": "#fbc02d", "sub": "전국평균", "date": datetime.now().strftime("%Y-%m-%d")})
    except:
        pass

    return items


# ─────────────────────────────────────────────
# 5. 헤더
# ─────────────────────────────────────────────
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div class="dash-header">
    <div class="dash-title">⚡ 국가 <span>에너지 및 산업</span> 핵심지표 대시보드</div>
    <div class="dash-subtitle">Energy Strategy &amp; Policy Planning Dashboard &nbsp;·&nbsp; v3.0 &nbsp;·&nbsp; 조회: {now_str}</div>
</div>
""", unsafe_allow_html=True)

col_r, col_info = st.columns([1, 6])
with col_r:
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_info:
    st.markdown(
        "<div style='padding-top:8px; font-size:12px; color:#546e7a;'>"
        "⏱ KPX 15분 · ECOS/KOSIS/Opinet 1시간 간격 자동 갱신</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ─────────────────────────────────────────────
# 6. 실시간 전력 수급 상단 요약 바
# ─────────────────────────────────────────────
# KPX 에러 상태 초기화
if 'kpx_error' not in st.session_state:
    st.session_state['kpx_error'] = None

try:
    pwr_list = get_realtime_pwr_detail()
    pwr = pwr_list[-1]
    supply_pct = round(pwr['curr'] / pwr['supp'] * 100, 1) if pwr['supp'] else 0

    # 캐시 데이터 사용 중 안내
    if st.session_state.get('kpx_error'):
        last_t = st.session_state.get('kpx_last_time', '알 수 없음')
        st.warning(f"⚠️ KPX API 연결 실패 — 마지막 성공 데이터 표시 중 (수집: {last_t})\n오류: {st.session_state['kpx_error']}", icon="🕐")

except Exception as e:
    st.markdown(f"<div class='error-box'>⚠️ 전력 데이터 오류: {e}</div>", unsafe_allow_html=True)
    pwr_list = []
    pwr = None
    supply_pct = 0

# ─────────────────────────────────────────────
# 7. KPI 카드 행
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>핵심 전략 지표</div>", unsafe_allow_html=True)

eco_items = get_strategic_data()
kpi_cols = st.columns(5)

with kpi_cols[0]:
    st.markdown("""
    <div class="kpi-card" style="border-top-color:#e91e63;">
        <div class="kpi-name">🚀 '26년 정부 R&D 예산</div>
        <div class="kpi-val">35.3<span class="kpi-unit">조원</span></div>
        <div class="kpi-sub" style="color:#e91e63;">▲ 전년比 19.3% 증가</div>
        <div class="kpi-date">📅 2026년 정부 예산안</div>
    </div>
    """, unsafe_allow_html=True)

for i, col in enumerate(kpi_cols[1:]):
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

# ─────────────────────────────────────────────
# 8. 신재생에너지 설비 현황
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>신재생에너지 설비 현황</div>", unsafe_allow_html=True)

re_df = pd.DataFrame([
    {"name": "태양광",   "MW": 30760.3},
    {"name": "풍력",     "MW": 2437.3},
    {"name": "바이오",   "MW": 2561.4},
    {"name": "수력",     "MW": 1815.4},
    {"name": "연료전지", "MW": 1289.8},
])

re_kpi_cols = st.columns(5)
re_cards = [
    {"name": "🌱 신재생에너지 총계", "value": "39,465.1", "unit": "MW", "color": "#00897b", "sub": "설비용량 합계", "date": "2025-12 기준"},
    {"name": "☀️ 태양광",           "value": "30,760.3", "unit": "MW", "color": "#fdd835", "sub": "전체의 77.9%",  "date": "2025-12 기준"},
    {"name": "💨 풍력",              "value": "2,437.3",  "unit": "MW", "color": "#29b6f6", "sub": "전체의 6.2%",   "date": "2025-12 기준"},
    {"name": "🌿 바이오",            "value": "2,561.4",  "unit": "MW", "color": "#66bb6a", "sub": "전체의 6.5%",   "date": "2025-12 기준"},
    {"name": "🔋 연료전지",          "value": "1,289.8",  "unit": "MW", "color": "#ab47bc", "sub": "전체의 3.3%",   "date": "2025-12 기준"},
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

# with st.expander("📊 신재생에너지 상세 차트 분석", expanded=False):
    # re_tab1, re_tab2 = st.tabs(["📊 에너지원별 비중", "📈 설비용량 비교"])
    # ...
    pass

# ─────────────────────────────────────────────
# 9. 실시간 전력 수급 현황
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>실시간 전력 수급 현황</div>", unsafe_allow_html=True)

pwr_cols = st.columns(3)
pwr_cards = [
    {"name": "🏭 발전설비용량",    "value": "158,147",               "unit": "MW", "color": "#42a5f5", "sub": "원자력 26,050 · 석탄 40,766 · 가스 45,705 · 신재생 39,790", "date": "2026-03 기준"},
    {"name": "⚡ 현재 전력 수요",  "value": f"{pwr['curr']:,.0f}"  if pwr else "-", "unit": "MW", "color": "#ff4b4b", "sub": "● LIVE",       "date": pwr['formatted_time'] if pwr else "-"},
    {"name": "🔌 공급능력",        "value": f"{pwr['supp']:,.0f}"  if pwr else "-", "unit": "MW", "color": "#00d4ff", "sub": "공급 가능량",   "date": pwr['formatted_time'] if pwr else "-"},
]
for i, col in enumerate(pwr_cols):
    card = pwr_cards[i]
    with col:
        if i == 0:
            # 발전설비용량 카드 — breakdown 라인 포함, 제목만 링크
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{card['color']}; height:130px;">
                <div class="kpi-name">
                    <a href="https://epsis.kpx.or.kr/epsisnew/selectEkpoBftChart.do?menuId=020100"
                       target="_blank"
                       style="color:#78909c; text-decoration:none;"
                       onmouseover="this.style.color='#42a5f5';"
                       onmouseout="this.style.color='#78909c';">
                        {card['name']} <span style="font-size:10px;">↗</span>
                    </a>
                </div>
                <div class="kpi-val">{card['value']}<span class="kpi-unit">{card['unit']}</span></div>
                <div style="font-size:10px; color:#78909c; margin-top:4px; line-height:1.5;">{card['sub']}</div>
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

# 토글: 수급 이력 + 추이 차트
# with st.expander("📊 전력 수급 상세 차트 분석", expanded=False):
    # if pwr_list:
    #     tab_hist, tab_trend = st.tabs(["📋 최근 수급 이력", "📈 전력 추이"])
    #     ...
    pass

# ─────────────────────────────────────────────
# 10. 푸터 + 자동 새로고침
# ─────────────────────────────────────────────
st.markdown(
    "<div class='footer'>"
    "데이터 출처: KPX(전력거래소) · ECOS(한국은행) · KOSIS(통계청) · Opinet(한국석유공사) · 정부 예산안<br>"
    "이 페이지는 15분마다 자동으로 새로고침됩니다."
    "</div>",
    unsafe_allow_html=True,
)
time.sleep(900)
st.rerun()
