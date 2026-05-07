from fastapi import FastAPI, HTTPException,Response
from collector import fetch_dividend_history, save_to_db
from analyzer import DividendAnalyzer
from ai_reporter import AIReporter
from sqlalchemy import text
from datetime import datetime, timedelta
from database import get_engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Dividend-Flow API")

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (로컬 테스트용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

analyzer = DividendAnalyzer()
reporter = AIReporter()

@app.get("/analyze/compare")
async def compare_stocks(tickers: str):
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    results = []
    for ticker in ticker_list:
        # 기존 분석 로직 호출
        data = await analyze_dividend_stock(ticker)
        results.append(data)
    return results

@app.get("/analyze/{ticker}")
async def analyze_dividend_stock(ticker: str):
    ticker = ticker.upper()
    engine = get_engine()

    # 1. 캐시 확인 (유효 기간: 24시간)
    with engine.connect() as conn:
        cache_query = text("""
            SELECT report_text, created_at 
            FROM ai_report_cache 
            WHERE ticker = :ticker
        """)
        result = conn.execute(cache_query, {"ticker": ticker}).fetchone()

    if result:
        report_text, created_at = result
        # 24시간이 지나지 않았다면 캐시된 리포트 반환
        if datetime.now() - created_at < timedelta(hours=24):
            # 분석 지표는 실시간성을 위해 새로 계산 (빠르니까)
            raw_data = analyzer.load_data(ticker)
            metrics = analyzer.calculate_metrics(raw_data, ticker)
            
            return {
                "ticker": ticker,
                "financial_metrics": metrics,
                "ai_insight": report_text,
                "source": "cache"  # 캐시에서 가져왔음을 명시
            }

    # 2. 캐시가 없거나 만료된 경우: 전체 파이프라인 가동
    df = fetch_dividend_history(ticker)
    if df is not None:
        save_to_db(df, ticker)

    raw_data = analyzer.load_data(ticker)
    if raw_data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    
    metrics = analyzer.calculate_metrics(raw_data, ticker)
    ai_insight = await reporter.generate_report(metrics)

    # 3. 새로운 리포트 DB에 저장 (UPSERT 로직)
    with engine.connect() as conn:
        upsert_query = text("""
            INSERT INTO ai_report_cache (ticker, report_text, created_at)
            VALUES (:ticker, :report, CURRENT_TIMESTAMP)
            ON CONFLICT (ticker) 
            DO UPDATE SET report_text = EXCLUDED.report_text, created_at = CURRENT_TIMESTAMP
        """)
        conn.execute(upsert_query, {"ticker": ticker, "report": ai_insight})
        conn.commit()

    return {
        "ticker": ticker,
        "financial_metrics": metrics,
        "ai_insight": ai_insight,
        "source": "api"
    }




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)