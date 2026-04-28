import pandas as pd
import numpy as np
from database import get_engine

class DividendAnalyzer:
    def __init__(self):
        self.engine = get_engine()

    def load_data(self, ticker_symbol):
        """DB에서 데이터를 로드하고 전처리 수행"""
        query = f"SELECT date, dividend FROM dividend_history WHERE ticker = '{ticker_symbol}'"
        df = pd.read_sql(query, self.engine)
        
        if df.empty:
            return None
            
        # Data Cleansing: 시계열 데이터 변환 및 정렬
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df.set_index('date', inplace=True)
        return df

    def calculate_metrics(self, df, ticker_symbol):
        """Vectorization을 활용한 핵심 지표 산출"""
        # 연단위 리샘플링 (연간 배당 합산)
        yearly_df = df.resample('YE').sum()
        
        # 현재 연도(2026년) 데이터 제외 (미완성 데이터 제거)
        # 데이터가 2026년까지 있다면, 2025년까지만 잘라서 분석에 사용
        current_year = pd.Timestamp.now().year
        clean_yearly = yearly_df[yearly_df.index.year < current_year]

        # CAGR (연평균 성장률) 계산 - Vectorized Operation
        # 공식: ((현재값 / 이전값) ** (1/n)) - 1
        if len(clean_yearly) >= 5:
            years = 5
            # 최근 5년치 데이터 추출 (예: 2021~2025)
            analysis_df = clean_yearly.iloc[-years:]
        
            start_val = analysis_df['dividend'].iloc[0]
            end_val = analysis_df['dividend'].iloc[-1]
        
            # CAGR 공식 적용 (4년 간의 성장 기간)
            cagr = ((end_val / start_val) ** (1 / (years - 1)) - 1) * 100
        else:
            cagr = None

        #배당 성장 지속성 (연속 상승 여부 체크)
        # 연속 성장 연수는 전체 데이터로 보되, 소수점 관리
        yearly_df['is_growth'] = yearly_df['dividend'].diff() > 0
        consecutive_growth = (yearly_df['is_growth'] == True).sum()

        return {
            "ticker": ticker_symbol,
            "cagr_5y": round(cagr, 2) if cagr else "N/A",
            "consecutive_years": consecutive_growth,
            "last_full_year_div": round(float(clean_yearly['dividend'].iloc[-1]), 4) if not clean_yearly.empty else 0
        }

if __name__ == "__main__":
    analyzer = DividendAnalyzer()
    target_tickers = ["SCHD", "JEPI", "AAPL"]

    for ticker in target_tickers:
        raw_data = analyzer.load_data(ticker)
        if raw_data is not None:
            metrics = analyzer.calculate_metrics(raw_data, ticker)
            print(f"📊 {ticker} 분석 결과: {metrics}")