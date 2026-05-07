import yfinance as yf
import pandas as pdfrom 
from database import get_engine, create_tables

def fetch_dividend_history(ticker_symbol):
    print(f"🚀 {ticker_symbol} 데이터 수집 시작...")
    ticker = yf.Ticker(ticker_symbol)
    
    try:
        # 1. dividends를 직접 부르는 대신 history를 호출
        # 이렇게 하면 내부적으로 _dividends 속성이 강제 생성
        hist = ticker.history(period="max")
        
        # 2. 히스토리 데이터 안에 'Dividends' 컬럼이 있는지 확인
        if "Dividends" in hist.columns:
            # 배당금이 발생한 날짜만 필터링 (0보다 큰 값)
            div_series = hist[hist["Dividends"] > 0]["Dividends"]
        else:
            # 만약 위 방식이 실패하면 기존 방식을 시도하되 예외처리
            div_series = ticker.get_dividends()

        if div_series.empty:
            print(f"⚠️ {ticker_symbol}: 배당 내역을 찾을 수 없습니다.")
            return None
            
        # 데이터프레임 형식으로 변환 (main logic과 호환)
        df = div_series.reset_index()
        df.columns = ['Date', 'Dividends']
        return df

    except Exception as e:
        print(f"❌ {ticker_symbol} 데이터 수집 중 오류 발생: {e}")
        return None
    
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