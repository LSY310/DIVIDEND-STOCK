#CAGR, 총수익률 등을 계산
import pandas as pd
from database import get_engine
import yfinance as yf
from datetime import datetime

class DividendAnalyzer:
    def __init__(self):
        self.engine = get_engine()

    def load_data(self, ticker_symbol):
        # 특정 종목의 데이터를 DB에서 읽어와 시계열 포맷으로 변환
        query = f"SELECT date, dividend FROM dividend_history WHERE ticker = '{ticker_symbol}'"
        df = pd.read_sql(query, self.engine)
        
        if df.empty:
            return None
            
        # Data Cleansing: 시계열 데이터 변환 및 정렬
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').set_index('date')
        return df

    def calculate_metrics(self, df, ticker_symbol):
        # 연도별로 데이터를 리샘플링하여 합산(연간 배당 합산)
        yearly_df = df.resample('YE').sum()
        
        # 현재 연도(2026년) 데이터 제외 (미완성 데이터 제거)
        # 데이터가 2026년까지 있다면, 2025년까지만 잘라서 분석에 사용
        clean_yearly = yearly_df[yearly_df.index.year < pd.Timestamp.now().year]

        # 5년 연평균 성장률(CAGR) 계산
        # 공식: ((현재값 / 이전값) ** (1/n)) - 1
        cagr = "N/A"
        if len(clean_yearly) >= 5:
            analysis_df = clean_yearly.iloc[-5:]
            v_start, v_end = analysis_df['dividend'].iloc[0], analysis_df['dividend'].iloc[-1]
            if v_start > 0:
                cagr = round(((v_end / v_start) ** (1/4) - 1) * 100, 2)

        # 배당이 전년보다 올랐는지 체크하여 연속 성장 연수를 구하는과정
        yearly_df['is_growth'] = yearly_df['dividend'].diff() > 0
        consecutive = int((yearly_df['is_growth'] == True).sum())

        # 추가 금융 지표 (yfinance.info 활용)
        t = yf.Ticker(ticker_symbol)
        info = t.info
        payout = round(info.get('payoutRatio', 0) * 100, 2)
        
        # 배당락일 포맷팅
        ex_date = datetime.fromtimestamp(info.get('exDividendDate')).strftime('%Y-%m-%d') if info.get('exDividendDate') else "N/A"
        
        # 1년 총 수익률 (주가 변동 + 배당 수익)
        hist_1y = t.history(period="1y")
        total_ret = 0.0
        if not hist_1y.empty:
            price_ret = (hist_1y['Close'].iloc[-1] - hist_1y['Close'].iloc[0]) / hist_1y['Close'].iloc[0]
            total_ret = round((price_ret + info.get('dividendYield', 0)) * 100, 2)

        return {
            "ticker": ticker_symbol, "cagr_5y": cagr, "consecutive_years": consecutive,
            "last_full_year_div": float(clean_yearly['dividend'].iloc[-1]) if not clean_yearly.empty else 0.0,
            "payout_ratio": payout, "total_return_1y": total_ret, "ex_dividend_date": ex_date
        }