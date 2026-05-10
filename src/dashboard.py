import streamlit as st
import requests
from ai_reporter import AIReporter

pdf_gen = AIReporter()


st.set_page_config(page_title="Dividend-Flow Pro", layout="wide")
st.title("📈 Dividend-Flow: AI 배당 분석 대시보드")

with st.sidebar:
    st.header("Search")
    tickers = st.text_input("분석할 티커 (예: SCHD, AAPL)", "SCHD, AAPL")
    btn = st.button("Deep Analysis 실행")

if btn:
    with st.spinner("데이터 분석 중..."):
        # 백엔드 API를 호출하여 결과를 가져온다
        res = requests.get(f"http://localhost:8000/analyze/compare?tickers={tickers}").json()
        
        for data in res:
            ticker = data['ticker']
            m = data['financial_metrics']
            
            # 종목별로 보기 좋게 접이식 박스로 구현
            with st.expander(f"📌 {ticker} 분석 리포트 (출처: {data['source']})", expanded=True):
                # 주요 지표를 상단에 가로로 배치
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("5년 CAGR", f"{m['cagr_5y']}%")
                c2.metric("성장연수", f"{m['consecutive_years']}년")
                c3.metric("최근배당", f"${m['last_full_year_div']}")
                c4.metric("배당성향", f"{m['payout_ratio']}%")
                c5.metric("총수익률", f"{m['total_return_1y']}%")
                c6.metric("배당락일", m['ex_dividend_date'])
                
                # AI가 작성한 상세 의견을 하단에 배치
                st.info(data['ai_insight'])

                st.download_button(
                    label="📝 리포트 텍스트로 저장",
                    data=data['ai_insight'],       # 분석 내용 문자열 그대로 전달
                    file_name=f"{ticker}_report.txt",
                    mime="text/plain"              # 파일 형식을 텍스트로 지정
)