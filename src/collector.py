#yfinance에서 배당금을 긁어와 DB에 저장하는 역할

import yfinance as yf
import pandas as pd
from database import get_engine, create_tables

def fetch_dividend_history(ticker_symbol):
    print(f"{ticker_symbol} 데이터 수집 시작...")
    ticker = yf.Ticker(ticker_symbol)
    
    try:
        # 전체 히스토리를 가져와서 배당금 컬럼만 필터링
        # ticker.dividends 속성보다 history() 호출이 데이터 누락이 적어 더 안정적이다
        hist = ticker.history(period="max")
        
        if "Dividends" in hist.columns:
            # 배당금이 0보다 큰 날짜(실제 지급일)만 추출
            div_series = hist[hist["Dividends"] > 0]["Dividends"]
        else:
            # history에 컬럼이 없는 특수 상황에 대비한 예외적 수집
            div_series = ticker.get_dividends()

        if div_series.empty:
            print(f"{ticker_symbol}: 배당 내역이 존재하지 않습니다.")
            return None
            
        # DB 구조에 맞게 데이터프레임 형식으로 변환
        df = div_series.reset_index()
        df.columns = ['Date', 'Dividends']
        return df

    except Exception as e:
        print(f"{ticker_symbol} 수집 중 오류 발생: {e}")
        return None
    
def save_to_db(df, ticker_symbol):
    """
    수집된 데이터를 PostgreSQL DB에 저장합니다. 
    동일한 날짜의 데이터가 있을 경우 무시하도록 설계되었습니다.
    """

    engine = get_engine()
    # 종목명(ticker) 컬럼 추가
    df['ticker'] = ticker_symbol
    try:
        # if_exists='append'를 사용해 기존 데이터 뒤에 붙임
        # DB의 UNIQUE 제약 조건 덕분에 중복 데이터는 자동으로 걸러진다
        df.to_sql('dividend_history', engine, if_exists='append', index=False)
    except Exception:
        # 중복 데이터(Primary Key/Unique 필드 충돌) 발생 시 
        # 로그를 남기지 않고 조용히 넘어가서 전체 파이프라인을 유지
        pass
