import yfinance as yf
import pandas as pdfrom 
from database import get_engine, create_tables

def fetch_dividend_history(ticker_symbol):
    print(f"🚀 {ticker_symbol} 데이터 수집 시작...")
    ticker = yf.Ticker(ticker_symbol)
    
    # 배당금 내역 가져오기
    div_history = ticker.dividends
    
    if div_history.empty:
        print("❌ 배당 내역이 없습니다.")
        return None
        
    # 데이터프레임으로 변환
    df = div_history.reset_index()
    df.columns = ['date', 'dividend']
    
    # 타임존 정보 제거 (DB 저장 시 발생할 수 있는 에러 방지)
    # tz_localize(None)을 통해 순수 시간 데이터로 변환
    df['date'] = df['date'].dt.tz_localize(None)

    print(f"수집 완료: {len(df)}건의 기록 발견")
    return df

def save_to_db(df, ticker_symbol):
    engine = get_engine()
    # 종목명(ticker) 컬럼 추가
    df['ticker'] = ticker_symbol
    # DB의 dividend_history 테이블에 데이터 밀어넣기
    try:
        df.to_sql('dividend_history', engine, if_exists='append', index=False)
        print(f"{ticker_symbol} 데이터 DB 저장 완료!")
    except Exception as e:
        print(f"저장 중 오류 발생 (중복 데이터일 가능성 높음): {e}")
        

if __name__ == "__main__":
    create_tables() # 테이블 먼저 만들고
    # 테스트하고 싶은 종목들 리스트
    target_tickers = ["SCHD", "JEPI", "AAPL"]

    for ticker in target_tickers:
        df = fetch_dividend_history(ticker)
        if df is not None:
            save_to_db(df, ticker)