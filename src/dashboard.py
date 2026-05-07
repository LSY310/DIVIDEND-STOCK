import streamlit as st
import requests
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="Dividend-Flow Dashboard", layout="wide")

st.title("📈 Dividend-Flow: AI 배당 분석 대시보드")
st.markdown("티커를 입력하면 실시간 지표 분석과 AI 인사이트를 제공합니다.")

# 사이드바: 종목 입력
with st.sidebar:
    st.header("🔍 종목 검색")
    target_tickers = st.text_input("티커 입력 (쉼표로 구분)", "SCHD, AAPL, JEPI")
    analyze_btn = st.button("분석 시작")

# 메인 화면 로직
if analyze_btn:
    with st.spinner("데이터를 분석하고 AI 리포트를 생성 중입니다..."):
        try:
            # 백엔드 API 호출 (URL 오타 주의!)
            response = requests.get(f"http://localhost:8000/analyze/compare?tickers={target_tickers}")
            
            if response.status_code == 200:
                results = response.json()
                
                # 여러 종목을 카드로 보여주기
                for res in results:
                    ticker = res['ticker']
                    metrics = res['financial_metrics']
                    insight = res['ai_insight']
                    
                    with st.expander(f"📌 {ticker} 분석 결과 확인하기", expanded=True):
                        col1, col2, col3 = st.columns([1, 1, 2])
                        
                        with col1:
                            st.metric("5년 CAGR", f"{metrics['cagr_5y']}%")
                            st.metric("연속 성장", f"{metrics['consecutive_years']}년")
                        
                        with col2:
                            st.metric("최근 배당금", f"${metrics['last_full_year_div']}")
                            # 캐시 여부 표시 (source가 백엔드에서 전달될 경우)
                            source = res.get('source', 'N/A')
                            st.caption(f"Data Source: {source}")
                            
                        with col3:
                            st.info("🤖 AI Insight")
                            st.markdown(insight)
                
                st.success("모든 분석이 완료되었습니다!")
            else:
                st.error(f"백엔드 에러: {response.status_code}")
                
        except Exception as e:
            st.error(f"연결 오류: 백엔드 서버(FastAPI)가 켜져 있는지 확인하세요. ({e})")