from fastapi import FastAPI, HTTPException,Response
from collector import fetch_dividend_history, save_to_db
from analyzer import DividendAnalyzer
from ai_reporter import AIReporter

app = FastAPI(title="Dividend-Flow API")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

analyzer = DividendAnalyzer()
reporter = AIReporter()

@app.get("/analyze/{ticker}")
async def analyze_dividend_stock(ticker: str):
    ticker = ticker.upper()
    
    # 1. 데이터 수집 및 갱신 (Extract & Load)
    df = fetch_dividend_history(ticker)
    if df is not None:
        save_to_db(df, ticker)
    else:
        # DB에 기존 데이터가 있는지 확인 시도 (생략 가능)
        pass

    # 2. 데이터 분석 (Transform)
    raw_data = analyzer.load_data(ticker)
    if raw_data is None:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    
    metrics = analyzer.calculate_metrics(raw_data, ticker)

    # 3. AI 리포트 생성 (Insight)
    ai_insight = await reporter.generate_report(metrics)

    return {
        "ticker": ticker,
        "financial_metrics": metrics,
        "ai_insight": ai_insight
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)