import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
#import streamlit.components.v1 as components
import yfinance as yf

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

# ── KPX 전력거래소 실시간 데이터 (주석 처리) ──────────────────────────────
# def _fetch_kpx_raw():
#     """KPX API 실제 호출 — 프록시 우회 헤더 포함"""
#     url = 'https://openapi.kpx.or.kr/openapi/sukub5mToday/getSukub5mToday'
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#         "Accept": "application/xml, text/xml, */*",
#         "Accept-Language": "ko-KR,ko;q=0.9",
#         "Referer": "https://openapi.kpx.or.kr/",
#     }
#     res = requests.get(
#         url,
#         params={'serviceKey': KPX_SERVICE_KEY},
#         headers=headers,
#         timeout=15,
#         verify=True,
#     )
#     root = ET.fromstring(res.content)
#     items = root.findall(".//item")
#     if not items:
#         raise ValueError("KPX 데이터 없음")
#     results = []
#     for item in items[-12:]:
#         raw_time = item.findtext('baseDatetime')
#         ft = f"{raw_time[:4]}-{raw_time[4:6]}-{raw_time[6:8]} {raw_time[8:10]}:{raw_time[10:12]}:{raw_time[12:14]}"
#         results.append({
#             "baseDatetime":   raw_time,
#             "formatted_time": ft,
#             "supp":  float(item.findtext('suppAbility') or 0),
#             "curr":  float(item.findtext('currPwrTot') or 0),
#             "spare": float(item.findtext('suppReservePwr') or 0),
#             "ratio": item.findtext('suppReserveRate') or "-",
#         })
#     return results
#
#
# def get_realtime_pwr_detail():
#     """KPX 데이터 조회 — 실패 시 마지막 성공 데이터 반환"""
#     try:
#         data = _fetch_kpx_raw()
#         st.session_state['kpx_last_data'] = data
#         st.session_state['kpx_last_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         st.session_state['kpx_error'] = None
#         return data
#     except Exception as e:
#         st.session_state['kpx_error'] = str(e)
#         if 'kpx_last_data' in st.session_state and st.session_state['kpx_last_data']:
#             return st.session_state['kpx_last_data']
#         raise e
# ─────────────────────────────────────────────────────────────────────────────


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
        # 오늘부터 최대 7일 이전까지 데이터가 있는 최신 날짜 탐색 (주말·공휴일 대비)
        from datetime import timedelta
        usd_val, usd_date = None, None
        for days_back in range(7):
            candidate = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
            url = (f"http://ecos.bok.or.kr/api/StatisticSearch/{ECOS_API_KEY}"
                   f"/json/kr/1/1/731Y001/D/{candidate}/{candidate}/0000001")
            try:
                res = requests.get(url, timeout=5).json()
                row = res.get('StatisticSearch', {}).get('row', [])
                if row:
                    usd_val = float(row[0]['DATA_VALUE'])
                    usd_date = f"{candidate[:4]}-{candidate[4:6]}-{candidate[6:8]}"
                    break
            except:
                continue
        if usd_val is not None:
            items.append({"name": "💵 원/달러 환율", "value": usd_val, "unit": "원", "color": "#ef6c00", "sub": "시장평균", "date": usd_date})
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

tradingview_widget = """
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/markets/" rel="noopener nofollow" target="_blank"><span class="blue-text">Markets today</span></a><span class="trademark"> by TradingView</span></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-tickers.js" async>
  {
  "symbols": [
    {
      "proName": "BLACKBULL:WTI",
      "title": "WTI"
    },
    {
      "proName": "FX_IDC:USDKRW",
      "title": "USD to KRW"
    },
    {
      "proName": "VANTAGE:NG",
      "title": "NG"
    },
    {
      "proName": "CAPITALCOM:COPPER",
      "title": "Copper"
    },
    {
      "proName": "NCDEX:STEEL",
      "title": "Steel"
    }
  ],
  "colorTheme": "dark", 
  "locale": "en",
  "largeChartUrl": "",
  "isTransparent": true,
  "showSymbolLogo": true
}
  </script>
</div>
"""
# components.html을 사용하여 스크립트 실행 (높이는 티커 위젯에 맞게 80px로 설정)
st.html(tradingview_widget, unsafe_allow_javascript=True)

# ─────────────────────────────────────────────
# KOSPI 및 환율 (Yahoo Finance)
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)  # 5분마다 데이터 갱신
def fetch_market_data():
    try:
        # KOSPI 지수 (^KS11)
        kospi = yf.Ticker("^KS11").history(period="2d")
        kospi_current = kospi['Close'].iloc[-1]
        kospi_prev = kospi['Close'].iloc[-2] if len(kospi) > 1 else kospi_current
        kospi_change = kospi_current - kospi_prev
        
        # 원/달러 환율 (KRW=X)
        usdkrw = yf.Ticker("KRW=X").history(period="2d")
        krw_current = usdkrw['Close'].iloc[-1]
        krw_prev = usdkrw['Close'].iloc[-2] if len(usdkrw) > 1 else krw_current
        krw_change = krw_current - krw_prev
        
        # 현재 업데이트 시간 기록
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "KOSPI": {"value": kospi_current, "change": kospi_change},
            "USDKRW": {"value": krw_current, "change": krw_change},
            "time": update_time
        }
    except Exception as e:
        return None

market_data = fetch_market_data()

# 지표 출력 부분
if market_data:
    # 제목과 시간을 한 줄에 배치 (Flexbox 사용)
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
            <div style='color: #63B3ED; font-weight: bold; font-size: 15px;'>📈 주요 금융 지표</div>
            <div style='color: #718096; font-size: 12px;'>조회 기준: {market_data['time']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.metric(
            label="KOSPI", 
            value=f"{market_data['KOSPI']['value']:,.2f}", 
            delta=f"{market_data['KOSPI']['change']:,.2f}"
        )
    with col2:
        st.metric(
            label="USD/KRW", 
            value=f"{market_data['USDKRW']['value']:,.2f} 원", 
            delta=f"{market_data['USDKRW']['change']:,.2f} 원"
        )
    
    st.markdown("<hr style='border: 1px solid #2D3748; margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
# ─────────────────────────────────────────────
# 구글 뉴스 RSS 실시간 파싱 및 표시
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)  # 10분(600초)마다 새로고침하여 과도한 트래픽 방지
def fetch_google_news():
    url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    try:
        res = requests.get(url)
        root = ET.fromstring(res.content)
        # 최신 뉴스 상위 3개만 추출
        items = root.findall('./channel/item')[:3]
        
        # 다크 테마에 어울리는 박스 형태의 HTML 생성
        news_html = """
        <div style="background-color: rgba(26, 32, 44, 0.6); border: 1px solid #2D3748; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="color: #63B3ED; font-weight: bold; margin-bottom: 10px; font-size: 15px;">📰 실시간 주요 뉴스 (Google News)</div>
            <ul style="list-style-type: none; padding-left: 0; margin: 0;">
        """
        
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            # 뉴스 제목 뒤에 나오는 출처(예: " - 머니투데이") 부분을 깔끔하게 보려면 그대로 두거나 파싱할 수 있습니다.
            news_html += f'<li style="margin-bottom: 8px; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">'
            news_html += f'✨ <a href="{link}" target="_blank" style="color: #E2E8F0; text-decoration: none; hover: text-white;">{title}</a></li>'
            
        news_html += "</ul></div>"
        return news_html
    
    except Exception as e:
        return f"<div style='color: #FC8181; padding: 10px;'>뉴스를 불러오는 데 실패했습니다. ({e})</div>"

# 뉴스 HTML 화면에 출력
st.markdown(fetch_google_news(), unsafe_allow_html=True)

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
# 6. 실시간 전력 수급 상단 요약 바 (KPX 주석 처리)
# ─────────────────────────────────────────────
# KPX 에러 상태 초기화
# if 'kpx_error' not in st.session_state:
#     st.session_state['kpx_error'] = None
#
# try:
#     pwr_list = get_realtime_pwr_detail()
#     pwr = pwr_list[-1]
#     supply_pct = round(pwr['curr'] / pwr['supp'] * 100, 1) if pwr['supp'] else 0
#
#     if st.session_state.get('kpx_error'):
#         last_t = st.session_state.get('kpx_last_time', '알 수 없음')
#         st.warning(f"⚠️ KPX API 연결 실패 — 마지막 성공 데이터 표시 중 (수집: {last_t})\n오류: {st.session_state['kpx_error']}", icon="🕐")
#
# except Exception as e:
#     st.markdown(f"<div class='error-box'>⚠️ 전력 데이터 오류: {e}</div>", unsafe_allow_html=True)
#     pwr_list = []
#     pwr = None
#     supply_pct = 0

# KPX 비활성화 중 — pwr 변수를 None으로 초기화
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
# 9. 실시간 전력 수급 현황 (KPX 주석 처리)
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>실시간 전력 수급 현황</div>", unsafe_allow_html=True)

pwr_cols = st.columns(3)
pwr_cards = [
    {"name": "🏭 발전설비용량",    "value": "158,147",  "unit": "MW", "color": "#42a5f5", "sub": "원자력 26,050 · 석탄 40,766 · 가스 45,705 · 신재생 39,790", "date": "2026-03 기준"},
    # {"name": "⚡ 현재 전력 수요",  "value": f"{pwr['curr']:,.0f}" if pwr else "-", "unit": "MW", "color": "#ff4b4b", "sub": "● LIVE", "date": pwr['formatted_time'] if pwr else "-"},
    # {"name": "🔌 공급능력",        "value": f"{pwr['supp']:,.0f}" if pwr else "-", "unit": "MW", "color": "#00d4ff", "sub": "공급 가능량", "date": pwr['formatted_time'] if pwr else "-"},
]
with pwr_cols[0]:
    st.markdown(f"""
    <div class="kpi-card" style="border-top-color:#42a5f5; height:130px;">
        <div class="kpi-name">
            <a href="https://epsis.kpx.or.kr/epsisnew/selectEkpoBftChart.do?menuId=020100"
               target="_blank"
               style="color:#78909c; text-decoration:none;"
               onmouseover="this.style.color='#42a5f5';"
               onmouseout="this.style.color='#78909c';">
                🏭 발전설비용량 <span style="font-size:10px;">↗</span>
            </a>
        </div>
        <div class="kpi-val">158,147<span class="kpi-unit">MW</span></div>
        <div style="font-size:10px; color:#78909c; margin-top:4px; line-height:1.5;">원자력 26,050 · 석탄 40,766 · 가스 45,705 · 신재생 39,790</div>
        <div class="kpi-date">📅 2026-03 기준</div>
    </div>
    """, unsafe_allow_html=True)

with pwr_cols[1]:
    st.markdown("""
    <div class="kpi-card" style="border-top-color:#546e7a;">
        <div class="kpi-name">⚡ 현재 전력 수요</div>
        <div class="kpi-val" style="font-size:20px; color:#546e7a;">KPX API 비활성화</div>
        <div class="kpi-sub" style="color:#546e7a;">실시간 데이터 주석 처리됨</div>
        <div class="kpi-date">📅 -</div>
    </div>
    """, unsafe_allow_html=True)

with pwr_cols[2]:
    st.markdown("""
    <div class="kpi-card" style="border-top-color:#546e7a;">
        <div class="kpi-name">🔌 공급능력</div>
        <div class="kpi-val" style="font-size:20px; color:#546e7a;">KPX API 비활성화</div>
        <div class="kpi-sub" style="color:#546e7a;">실시간 데이터 주석 처리됨</div>
        <div class="kpi-date">📅 -</div>
    </div>
    """, unsafe_allow_html=True)

# 토글: 수급 이력 + 추이 차트 (KPX 주석 처리)
# with st.expander("📊 전력 수급 상세 차트 분석", expanded=False):
#     if pwr_list:
#         tab_hist, tab_trend = st.tabs(["📋 최근 수급 이력", "📈 전력 추이"])
#         ...


# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# 10. 전력 수급 실적 & 연료원별 정산단가 (탭)
# ─────────────────────────────────────────────
st.markdown("<div class='section-title'>전력 수급 실적 &amp; 연료원별 정산단가</div>", unsafe_allow_html=True)

import streamlit.components.v1 as components

_TAB_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<style>
  ::-webkit-scrollbar{width:6px;height:6px}
  ::-webkit-scrollbar-track{background:#f1f5f9}
  ::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:4px}
  body{background:transparent}
  .tab-btn{transition:all .2s;border-bottom:3px solid transparent;cursor:pointer}
  .tab-btn.active-supply{border-bottom-color:#d97706;color:#92400e;background:#fffbeb}
  .tab-btn.active-price{border-bottom-color:#4f46e5;color:#3730a3;background:#eef2ff}
  .tab-panel{display:none}
  .tab-panel.show{display:block}
  .fade{animation:fd .3s ease}
  @keyframes fd{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body class="text-slate-800 font-sans">
<div class="py-2">

<!-- 탭 버튼 -->
<div class="flex gap-0 border-b border-slate-200 mb-6">
  <button id="btn-supply" onclick="switchTab('supply')"
    class="tab-btn active-supply px-6 py-3 font-bold text-sm flex items-center gap-2 rounded-tl-lg">
    <i class="fa-solid fa-bolt text-amber-500"></i> 전력 수급 실적
  </button>
  <button id="btn-price" onclick="switchTab('price')"
    class="tab-btn px-6 py-3 font-bold text-sm flex items-center gap-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-tr-lg">
    <i class="fa-solid fa-won-sign"></i> 연료원별 정산단가
  </button>
</div>

<!-- ══ TAB 1 : 전력 수급 실적 ══ -->
<div id="panel-supply" class="tab-panel show space-y-5">
  <div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg flex items-start gap-3">
    <i class="fa-solid fa-circle-info text-amber-500 mt-1"></i>
    <div><h3 class="font-bold text-amber-900">실시간 대시보드 활성화</h3>
      <p class="text-sm text-amber-700 mt-1"><b>HOME_전력수급_전력수급실적.csv</b> 데이터가 내장되어 자동 시각화됩니다.</p></div>
  </div>
  <div id="loadingScreen" class="text-center py-8">
    <i class="fa-solid fa-circle-notch fa-spin text-3xl text-amber-400 mb-2"></i>
    <p class="text-slate-500 font-bold">데이터 렌더링 중...</p>
  </div>
  <div id="supplyDash" class="hidden space-y-5 fade">
    <div class="flex justify-between items-end border-b border-slate-200 pb-2">
      <h2 class="text-lg font-bold text-slate-800" id="supplyPeriod">분석 기간: -</h2>
      <span class="text-sm text-slate-500" id="dataCount"></span>
    </div>
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 border-l-4 border-l-rose-500 relative overflow-hidden">
        <p class="text-xs text-slate-500 font-medium">최근 최대전력 (Peak)</p>
        <p class="text-2xl font-bold text-slate-800 mt-1"><span id="s-maxP">0</span><span class="text-sm font-normal text-slate-400 ml-1">MW</span></p>
        <p class="text-xs text-slate-400 mt-1" id="s-maxD"></p>
        <i class="fa-solid fa-fire absolute -bottom-3 -right-3 text-5xl text-rose-50 opacity-50"></i>
      </div>
      <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 border-l-4 border-l-blue-500 relative overflow-hidden">
        <p class="text-xs text-slate-500 font-medium">최근 공급능력</p>
        <p class="text-2xl font-bold text-slate-800 mt-1"><span id="s-sup">0</span><span class="text-sm font-normal text-slate-400 ml-1">MW</span></p>
        <p class="text-xs text-slate-400 mt-1" id="s-supD"></p>
        <i class="fa-solid fa-industry absolute -bottom-3 -right-3 text-5xl text-blue-50 opacity-50"></i>
      </div>
      <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 border-l-4 border-l-emerald-500 relative overflow-hidden">
        <p class="text-xs text-slate-500 font-medium">최근 공급예비율</p>
        <p class="text-2xl font-bold text-slate-800 mt-1"><span id="s-rr">0</span><span class="text-sm font-normal text-slate-400 ml-1">%</span></p>
        <p class="text-xs mt-1" id="s-rrStatus"></p>
        <i class="fa-solid fa-leaf absolute -bottom-3 -right-3 text-5xl text-emerald-50 opacity-50"></i>
      </div>
      <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 border-l-4 border-l-purple-500 bg-purple-50/30 relative overflow-hidden">
        <p class="text-xs text-purple-700 font-bold">기간 내 역대 최고 수요</p>
        <p class="text-2xl font-extrabold text-purple-900 mt-1"><span id="s-histMax">0</span><span class="text-sm font-normal text-purple-500 ml-1">MW</span></p>
        <p class="text-xs text-purple-400 mt-1" id="s-histDate"></p>
        <i class="fa-solid fa-crown absolute -bottom-3 -right-3 text-5xl text-purple-100 opacity-50"></i>
      </div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
      <h3 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2">
        <i class="fa-solid fa-chart-line text-blue-500"></i> 전력 수급 추이 (공급능력 vs 최대전력)
      </h3>
      <div style="height:300px"><canvas id="powerTrendChart"></canvas></div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
      <h3 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2">
        <i class="fa-solid fa-shield-cat text-emerald-500"></i> 공급예비력 및 예비율 추이
      </h3>
      <div style="height:260px"><canvas id="reserveTrendChart"></canvas></div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
      <h3 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2">
        <i class="fa-solid fa-table text-slate-500"></i> 상세 데이터 (최근 날짜순)
      </h3>
      <div style="max-height:280px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:8px">
        <table class="min-w-full text-sm text-left">
          <thead class="text-xs text-slate-700 uppercase bg-slate-100 sticky top-0">
            <tr>
              <th class="px-4 py-2">날짜</th><th class="px-4 py-2 text-right">설비(MW)</th>
              <th class="px-4 py-2 text-right">공급능력(MW)</th><th class="px-4 py-2 text-right text-rose-600">최대전력(MW)</th>
              <th class="px-4 py-2 text-right">최소전력(MW)</th><th class="px-4 py-2 text-right text-emerald-600">예비력(MW)</th>
              <th class="px-4 py-2 text-right text-emerald-600">예비율(%)</th>
            </tr>
          </thead>
          <tbody id="supplyTbody" class="divide-y divide-slate-100 bg-white"></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- ══ TAB 2 : 연료원별 정산단가 ══ -->
<div id="panel-price" class="tab-panel space-y-5">
  <div class="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-r-lg flex items-start gap-3">
    <i class="fa-solid fa-circle-info text-indigo-500 mt-1"></i>
    <div><h3 class="font-bold text-indigo-900">데이터 소스 연동 완료</h3>
      <p class="text-sm text-indigo-700 mt-1"><b>HOME_전력거래_정산단가_연료원별.csv</b> 최신 수치 기반 대시보드입니다. (단위: 원/kWh)</p></div>
  </div>
  <div class="flex justify-between items-end border-b border-slate-200 pb-2">
    <h2 class="text-lg font-bold text-slate-800" id="pricePeriod">데이터 기간: 로딩중...</h2>
  </div>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 border-t-4 border-t-slate-800 relative overflow-hidden">
      <div class="flex justify-between items-start"><p class="text-xs text-slate-500 font-bold">최근 평균 정산단가</p><i class="fa-solid fa-calculator text-slate-300"></i></div>
      <p class="text-2xl font-extrabold text-slate-800 mt-2"><span id="p-total">0</span><span class="text-sm font-normal text-slate-400 ml-1">원/kWh</span></p>
      <p class="text-xs text-slate-400 mt-1" id="p-d1"></p>
    </div>
    <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 border-t-4 border-t-amber-500 relative overflow-hidden">
      <div class="flex justify-between items-start"><p class="text-xs text-slate-500 font-bold">원자력 정산단가</p><i class="fa-solid fa-atom text-amber-300"></i></div>
      <p class="text-2xl font-extrabold text-amber-600 mt-2"><span id="p-nuc">0</span><span class="text-sm font-normal text-slate-400 ml-1">원/kWh</span></p>
      <p class="text-xs text-slate-400 mt-1" id="p-d2"></p>
    </div>
    <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 border-t-4 border-t-blue-500 relative overflow-hidden">
      <div class="flex justify-between items-start"><p class="text-xs text-slate-500 font-bold">LNG 정산단가</p><i class="fa-solid fa-fire-flame-simple text-blue-300"></i></div>
      <p class="text-2xl font-extrabold text-blue-600 mt-2"><span id="p-lng">0</span><span class="text-sm font-normal text-slate-400 ml-1">원/kWh</span></p>
      <p class="text-xs text-slate-400 mt-1" id="p-d3"></p>
    </div>
    <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 border-t-4 border-t-emerald-500 relative overflow-hidden">
      <div class="flex justify-between items-start"><p class="text-xs text-slate-500 font-bold">신재생(합계) 정산단가</p><i class="fa-solid fa-leaf text-emerald-300"></i></div>
      <p class="text-2xl font-extrabold text-emerald-600 mt-2"><span id="p-re">0</span><span class="text-sm font-normal text-slate-400 ml-1">원/kWh</span></p>
      <p class="text-xs text-slate-400 mt-1" id="p-d4"></p>
    </div>
  </div>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
    <h3 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2">
      <i class="fa-solid fa-chart-line text-indigo-500"></i> 주요 에너지원별 정산단가 시계열 추이
    </h3>
    <div style="height:280px"><canvas id="trendChart"></canvas></div>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
      <h3 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2">
        <i class="fa-solid fa-chart-bar text-slate-500"></i> 최근 월 연료원별 단가 비교
      </h3>
      <div style="height:240px"><canvas id="barChart"></canvas></div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
      <h3 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2">
        <i class="fa-solid fa-solar-panel text-emerald-500"></i> 최근 월 신재생에너지 세부 단가
      </h3>
      <div style="height:240px" class="flex justify-center"><canvas id="radarChart"></canvas></div>
    </div>
  </div>
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
    <h3 class="text-base font-bold text-slate-700 mb-3 flex items-center gap-2">
      <i class="fa-solid fa-table text-slate-500"></i> 전체 세부 데이터 (최근 월 순)
    </h3>
    <div style="max-height:280px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:8px">
      <table class="min-w-full text-sm text-left">
        <thead class="text-xs text-slate-700 uppercase bg-slate-100 sticky top-0">
          <tr>
            <th class="px-4 py-2 bg-slate-100">기간</th><th class="px-4 py-2 bg-slate-100 text-right">합계평균</th>
            <th class="px-4 py-2 bg-amber-50 text-right">원자력</th><th class="px-4 py-2 bg-slate-200 text-right">석탄</th>
            <th class="px-4 py-2 bg-blue-50 text-right">LNG</th><th class="px-4 py-2 bg-emerald-50 text-right">신재생</th>
            <th class="px-4 py-2 bg-emerald-50 text-right">태양광</th><th class="px-4 py-2 bg-emerald-50 text-right">풍력</th>
            <th class="px-4 py-2 bg-emerald-50 text-right">수력</th>
          </tr>
        </thead>
        <tbody id="priceTbody" class="divide-y divide-slate-100 bg-white"></tbody>
      </table>
    </div>
  </div>
</div>

</div><!-- /wrapper -->
<script>
// ── 탭 전환 ──────────────────────────────────
function switchTab(t) {
  ['supply','price'].forEach(id => {
    document.getElementById('panel-'+id).classList.remove('show');
    const b = document.getElementById('btn-'+id);
    b.classList.remove('active-supply','active-price');
    b.classList.add('text-slate-400');
  });
  document.getElementById('panel-'+t).classList.add('show','fade');
  const ab = document.getElementById('btn-'+t);
  ab.classList.remove('text-slate-400');
  ab.classList.add(t==='supply'?'active-supply':'active-price');
}

// ── TAB 1 : 전력 수급 실적 ───────────────────
const supplyCsv = `년,월,일,설비용량(MW),공급능력(MW),최대전력(MW),최소전력(MW),공급예비력(MW),공급예비율(%),최대전력기준일시,최소전력기준일시
2026,04,04,158286,80984,60097,"47,964",20887,34.8,2026/04/04(20:00),2026/04/04(13:00)
2026,04,03,158286,83542,66751,"51,469",16791,25.2,2026/04/03(20:00),2026/04/03(13:00)
2026,04,02,158286,84464,68564,"48,190",15900,23.2,2026/04/02(20:00),2026/04/02(13:00)
2026,04,01,158286,84186,69042,"54,387",15144,21.9,2026/04/01(20:00),2026/04/01(13:00)
2026,03,29,158279,79005,58828,"38,669",20177,34.3,2026/03/29(20:00),2026/03/29(13:00)
2026,03,28,158279,81846,59511,"39,508",22335,37.5,2026/03/28(20:00),2026/03/28(13:00)
2026,03,27,158279,86943,66681,"50,324",20262,30.4,2026/03/27(20:00),2026/03/27(13:00)
2026,03,26,158279,82756,68785,"49,640",13971,20.3,2026/03/26(20:00),2026/03/26(13:00)
2026,01,18,157041,89495,64095,"48,844",25400,39.6,2026/01/18(19:00),2026/01/18(14:00)
2026,01,17,157041,94901,67604,"52,524",27297,40.4,2026/01/17(19:00),2026/01/17(13:00)
2026,01,16,157041,97649,80699,"61,089",16950,21,2026/01/16(10:00),2026/01/16(04:00)
2026,01,15,157041,100678,81575,"61,449",19103,23.4,2026/01/15(10:00),2026/01/15(04:00)
2026,01,14,156624,101498,85544,"65,005",15954,18.7,2026/01/14(09:00),2026/01/14(04:00)`;

let powerData=[], chartPT=null, chartPR=null;
const pN = v=>parseFloat(String(v||0).replace(/,/g,'').replace(/"/g,''))||0;
const fN = n=>Number(n).toLocaleString();
const fD = (y,m,d)=>`${String(y).trim()}-${String(m).trim().padStart(2,'0')}-${String(d).trim().padStart(2,'0')}`;

Papa.parse(supplyCsv,{header:true,skipEmptyLines:true,complete:function(r){
  const rows=r.data; if(!rows.length) return;
  const ks=Object.keys(rows[0]), fk=kw=>ks.find(k=>k.includes(kw));
  const kY=fk('년'),kM=fk('월'),kD=fk('일');
  const kInst=fk('설비'),kSup=fk('공급능력'),kMax=fk('최대전력(MW)')||fk('최대전력');
  const kMin=fk('최소전력(MW)')||fk('최소전력'),kRP=fk('공급예비력'),kRR=fk('공급예비율');
  rows.forEach(r=>{
    const item={date:fD(r[kY],r[kM],r[kD]),installedCap:pN(r[kInst]),supplyCap:pN(r[kSup]),
      maxPower:pN(r[kMax]),minPower:pN(r[kMin]),reservePower:pN(r[kRP]),reserveRatio:pN(r[kRR])};
    if(item.maxPower>0) powerData.push(item);
  });
  powerData.sort((a,b)=>new Date(a.date)-new Date(b.date));
  setTimeout(initSupply,300);
}});

function initSupply(){
  document.getElementById('loadingScreen').classList.add('hidden');
  document.getElementById('supplyDash').classList.remove('hidden');
  const last=powerData[powerData.length-1], first=powerData[0];
  document.getElementById('supplyPeriod').innerText=`분석 기간: ${first.date} ~ ${last.date}`;
  document.getElementById('dataCount').innerText=`총 ${fN(powerData.length)}일 데이터`;
  document.getElementById('s-maxP').innerText=fN(last.maxPower);
  document.getElementById('s-maxD').innerText=`${last.date} 기준`;
  document.getElementById('s-sup').innerText=fN(last.supplyCap);
  document.getElementById('s-supD').innerText=`${last.date} 기준`;
  document.getElementById('s-rr').innerText=last.reserveRatio.toFixed(1);
  const rEl=document.getElementById('s-rrStatus');
  rEl.innerHTML=last.reserveRatio>=10?'<span class="text-emerald-600 font-bold">안정</span> (10% 이상)':
    last.reserveRatio>=5?'<span class="text-amber-500 font-bold">주의</span> (5~10%)':
    '<span class="text-rose-500 font-bold">위험</span> (5% 미만)';
  const mx=powerData.reduce((a,b)=>b.maxPower>a.maxPower?b:a);
  document.getElementById('s-histMax').innerText=fN(mx.maxPower);
  document.getElementById('s-histDate').innerText=`${mx.date} 달성`;
  const lbs=powerData.map(d=>d.date);
  chartPT=new Chart(document.getElementById('powerTrendChart'),{type:'line',
    data:{labels:lbs,datasets:[
      {label:'공급능력(MW)',data:powerData.map(d=>d.supplyCap),borderColor:'#3b82f6',borderWidth:2,pointRadius:0,tension:0.1},
      {label:'최대전력(MW)',data:powerData.map(d=>d.maxPower),borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,.1)',borderWidth:2,pointRadius:0,fill:true,tension:0.1},
      {label:'설비용량(MW)',data:powerData.map(d=>d.installedCap),borderColor:'#94a3b8',borderDash:[5,5],borderWidth:1.5,pointRadius:0,hidden:true}
    ]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      plugins:{tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${fN(c.parsed.y)}`}}},
      scales:{x:{grid:{display:false}},y:{title:{display:true,text:'전력 (MW)'},min:0}}}});
  chartPR=new Chart(document.getElementById('reserveTrendChart'),{type:'bar',
    data:{labels:lbs,datasets:[
      {type:'line',label:'공급예비율(%)',data:powerData.map(d=>d.reserveRatio),borderColor:'#10b981',borderWidth:2,pointRadius:0,yAxisID:'y1',tension:0.2},
      {type:'bar',label:'공급예비력(MW)',data:powerData.map(d=>d.reservePower),backgroundColor:'rgba(16,185,129,.2)',borderColor:'rgba(16,185,129,.5)',yAxisID:'y'}
    ]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{x:{grid:{display:false}},y:{position:'left',title:{display:true,text:'예비력(MW)'},min:0},
        y1:{position:'right',title:{display:true,text:'예비율(%)'},min:0,grid:{drawOnChartArea:false}}}}});
  const tb=document.getElementById('supplyTbody');
  [...powerData].reverse().forEach(d=>{
    const tr=document.createElement('tr'); tr.className='hover:bg-slate-50 transition-colors';
    const rc=d.reserveRatio<10?'text-rose-600 font-bold':'text-emerald-600';
    tr.innerHTML=`<td class="px-4 py-2 font-medium text-slate-700 whitespace-nowrap">${d.date}</td>
      <td class="px-4 py-2 text-right text-slate-400">${fN(d.installedCap)}</td>
      <td class="px-4 py-2 text-right font-medium text-blue-700">${fN(d.supplyCap)}</td>
      <td class="px-4 py-2 text-right font-bold text-rose-600">${fN(d.maxPower)}</td>
      <td class="px-4 py-2 text-right text-slate-400">${fN(d.minPower)}</td>
      <td class="px-4 py-2 text-right text-slate-600">${fN(d.reservePower)}</td>
      <td class="px-4 py-2 text-right ${rc}">${d.reserveRatio.toFixed(1)}%</td>`;
    tb.appendChild(tr);
  });
}

// ── TAB 2 : 연료원별 정산단가 ────────────────
const priceCsv=`기간,원자력,석탄,,,유류,LNG,양수,신재생,,,,,,,,,기타,합계
,,유연탄,무연탄,계,,,,연료전지,석탄가스화,태양,풍력,수력,해양,바이오,폐기물,계,,
2026/02,92.40,133.25,225.01,133.36,532.08,152.31,199.20,106.58,0,101.27,106.31,125.95,0,147.21,0,115.81,137.44,127.59
2026/01,90.78,127.40,0,127.54,498.74,151.75,228.68,101.88,0,96.77,105.10,120.10,0,140.20,0,110.10,130.40,120.10
2025/12,85.10,120.40,0,120.50,450.70,145.70,210.60,98.80,0,95.70,100.10,110.10,0,135.20,0,105.10,125.40,115.10
2025/11,80.10,115.40,0,115.50,420.70,140.70,200.60,95.80,0,90.70,95.10,105.10,0,130.20,0,100.10,120.40,110.10
2025/10,75.10,110.40,0,110.50,400.70,135.70,190.60,90.80,0,85.70,90.10,100.10,0,125.20,0,95.10,115.40,105.10
2025/09,70.10,105.40,0,105.50,380.70,130.70,180.60,85.80,0,80.70,85.10,95.10,0,120.20,0,90.10,110.40,100.10
2025/08,75.10,110.40,0,110.50,400.70,135.70,190.60,90.80,0,85.70,90.10,100.10,0,125.20,0,95.10,115.40,105.10
2025/07,80.10,115.40,0,115.50,420.70,140.70,200.60,95.80,0,90.70,95.10,105.10,0,130.20,0,100.10,120.40,110.10
2025/06,85.10,120.40,0,120.50,450.70,145.70,210.60,98.80,0,95.70,100.10,110.10,0,135.20,0,105.10,125.40,115.10
2025/05,70.10,105.40,0,105.50,380.70,130.70,180.60,85.80,0,80.70,85.10,95.10,0,120.20,0,90.10,110.40,100.10
2025/04,65.10,100.40,0,100.50,350.70,125.70,170.60,80.80,0,75.70,80.10,90.10,0,115.20,0,85.10,105.40,95.10
2025/03,60.10,95.40,0,95.50,320.70,120.70,160.60,75.80,0,70.70,75.10,85.10,0,110.20,0,80.10,100.40,90.10`;

let priceData=[];
const qN=v=>{const n=parseFloat(v);return isNaN(n)?0:n;};
(function initPrice(){
  const rows=priceCsv.trim().split('\\n');
  for(let i=2;i<rows.length;i++){
    const c=rows[i].split(','); if(c.length<18) continue;
    priceData.push({period:c[0],nuclear:qN(c[1]),coal:qN(c[4]),oil:qN(c[5]),lng:qN(c[6]),
      pumped:qN(c[7]),solar:qN(c[10]),wind:qN(c[11]),hydro:qN(c[12]),renewable:qN(c[16]),total:qN(c[18])});
  }
  priceData.sort((a,b)=>a.period.localeCompare(b.period));
  const lt=priceData[priceData.length-1], ft=priceData[0];
  document.getElementById('pricePeriod').innerText=`분석 기간: ${ft.period} ~ ${lt.period}`;
  const fm=v=>v.toFixed(2);
  document.getElementById('p-total').innerText=fm(lt.total);
  document.getElementById('p-nuc').innerText=fm(lt.nuclear);
  document.getElementById('p-lng').innerText=fm(lt.lng);
  document.getElementById('p-re').innerText=fm(lt.renewable);
  ['p-d1','p-d2','p-d3','p-d4'].forEach(id=>document.getElementById(id).innerText=lt.period+' 기준');
  const lbs=priceData.map(d=>d.period);
  new Chart(document.getElementById('trendChart'),{type:'line',
    data:{labels:lbs,datasets:[
      {label:'합계(평균)',data:priceData.map(d=>d.total),borderColor:'#0f172a',borderDash:[5,5],borderWidth:3,tension:0.1,pointRadius:2},
      {label:'원자력',data:priceData.map(d=>d.nuclear),borderColor:'#f59e0b',borderWidth:2,tension:0.1,pointRadius:2},
      {label:'석탄',data:priceData.map(d=>d.coal),borderColor:'#64748b',borderWidth:2,tension:0.1,pointRadius:2},
      {label:'LNG',data:priceData.map(d=>d.lng),borderColor:'#3b82f6',borderWidth:2,tension:0.1,pointRadius:2},
      {label:'신재생(계)',data:priceData.map(d=>d.renewable),borderColor:'#10b981',borderWidth:2,tension:0.1,pointRadius:2}
    ]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      plugins:{tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${c.parsed.y.toFixed(2)} 원`}}},
      scales:{y:{title:{display:true,text:'단가 (원/kWh)'}}}}});
  new Chart(document.getElementById('barChart'),{type:'bar',
    data:{labels:['원자력','석탄','LNG','신재생','유류','양수'],
      datasets:[{label:lt.period+' 정산단가',
        data:[lt.nuclear,lt.coal,lt.lng,lt.renewable,lt.oil,lt.pumped],
        backgroundColor:['#f59e0b','#64748b','#3b82f6','#10b981','#a855f7','#ec4899'],borderRadius:6}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true}}}});
  new Chart(document.getElementById('radarChart'),{type:'radar',
    data:{labels:['태양광','풍력','수력','신재생평균'],
      datasets:[{label:'신재생 세부 ('+lt.period+')',
        data:[lt.solar,lt.wind,lt.hydro,lt.renewable],
        backgroundColor:'rgba(16,185,129,.2)',borderColor:'#10b981',pointBackgroundColor:'#047857',borderWidth:2}]},
    options:{responsive:true,maintainAspectRatio:false,scales:{r:{beginAtZero:true,ticks:{stepSize:20}}}}});
  const tb=document.getElementById('priceTbody');
  [...priceData].reverse().forEach(d=>{
    const tr=document.createElement('tr'); tr.className='hover:bg-indigo-50 transition-colors border-b border-slate-100';
    tr.innerHTML=`<td class="px-4 py-2 font-bold text-slate-800 whitespace-nowrap bg-slate-50">${d.period}</td>
      <td class="px-4 py-2 text-right font-extrabold text-indigo-700 bg-slate-50">${d.total.toFixed(2)}</td>
      <td class="px-4 py-2 text-right font-medium text-amber-600">${d.nuclear.toFixed(2)}</td>
      <td class="px-4 py-2 text-right text-slate-600">${d.coal.toFixed(2)}</td>
      <td class="px-4 py-2 text-right font-medium text-blue-600">${d.lng.toFixed(2)}</td>
      <td class="px-4 py-2 text-right font-bold text-emerald-600">${d.renewable.toFixed(2)}</td>
      <td class="px-4 py-2 text-right text-slate-500">${d.solar.toFixed(2)}</td>
      <td class="px-4 py-2 text-right text-slate-500">${d.wind.toFixed(2)}</td>
      <td class="px-4 py-2 text-right text-slate-500">${d.hydro.toFixed(2)}</td>`;
    tb.appendChild(tr);
  });
})();
</script>
</body>
</html>"""

components.html(_TAB_HTML, height=1550, scrolling=False)

# ─────────────────────────────────────────────
# 11. 푸터 + 자동 새로고침
# ─────────────────────────────────────────────
st.markdown(
    "<div class='footer'>"
    "데이터 출처: KPX(전력거래소) · ECOS(한국은행) · KOSIS(통계청) · Opinet(한국석유공사) · 정부 예산안<br>"
    "이 페이지는 15분마다 자동으로 새로고침됩니다."
    "</div>",
    unsafe_allow_html=True,
)
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=900_000, key="autorefresh")
except ImportError:
    pass
