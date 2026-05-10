#전체 워크플로우를 제어하고 API 엔드포인트를 제공
import asyncio
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from sqlalchemy import text

# 내부 모듈 로드
from database import get_engine, create_tables
from collector import fetch_dividend_history, save_to_db
from analyzer import DividendAnalyzer
from ai_reporter import AIReporter
from models import AnalysisResponse, DividendMetrics # DividendMetrics 추가

app = FastAPI(title="Dividend-Flow API")

#CORS 설정: 프론트엔드와의 통신을 위해 필수
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 분석 및 리포트 객체 초기화
analyzer = DividendAnalyzer()
reporter = AIReporter()

@app.on_event("startup")
def on_startup():
    # 서버 실행 시 DB 테이블이 없으면 자동으로 생성
    create_tables()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # 브라우저의 파비콘 요청으로 인한 404 로그 방지
    return Response(status_code=204)

@app.get("/analyze/compare")
async def compare_stocks(tickers: str):
    """
    여러 종목을 동시에 비동기(Async)로 분석하여 응답 속도를 최적화합니다.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    # 각 종목 분석을 태스크로 만들어 병렬 실행
    tasks = [analyze_dividend_stock(ticker) for ticker in ticker_list]
    return await asyncio.gather(*tasks)

@app.get("/analyze/{ticker}", response_model=AnalysisResponse)
async def analyze_dividend_stock(ticker: str):
    """
    단일 종목에 대한 데이터 수집, 분석, AI 리포트 생성을 수행합니다.
    캐시(24시간)가 있다면 캐시를 우선 활용합니다.
    """
    ticker = ticker.upper()
    engine = get_engine()
    
    ai_insight = None
    source = "api"

    # DB 캐시 확인 (부하 감소)
    with engine.connect() as conn:
        cache_query = text("SELECT report_text, created_at FROM ai_report_cache WHERE ticker = :ticker")
        result = conn.execute(cache_query, {"ticker": ticker}).fetchone()

    if result:
        report_text, created_at = result
        # 캐시 유효기간 24시간 체크
        if datetime.now() - created_at < timedelta(hours=24):
            ai_insight = report_text
            source = "cache"

    # 캐시가 없거나 만료된 경우: 수집 및 분석 파이프라인 가동
    if not ai_insight:
        # 데이터 수집 (yfinance)
        df = fetch_dividend_history(ticker)
        if df is not None:
            save_to_db(df, ticker)

        # 수집된 원천 데이터를 분석 엔진으로 로드
        raw_data = analyzer.load_data(ticker)
        if raw_data is None:
            raise HTTPException(status_code=404, detail=f"{ticker} 데이터를 찾을 수 없습니다.")
        
        # 퀀트 지표 계산 (CAGR, 총수익률 등)
        metrics = analyzer.calculate_metrics(raw_data, ticker)
        # AI 전문가 리포트 생성
        ai_insight = await reporter.generate_report(metrics)

        # 생성된 리포트를 DB에 업데이트 (UPSERT)
        with engine.connect() as conn:
            upsert_query = text("""
                INSERT INTO ai_report_cache (ticker, report_text, created_at)
                VALUES (:ticker, :report, CURRENT_TIMESTAMP)
                ON CONFLICT (ticker) 
                DO UPDATE SET report_text = EXCLUDED.report_text, created_at = CURRENT_TIMESTAMP
            """)
            conn.execute(upsert_query, {"ticker": ticker, "report": ai_insight})
            conn.commit()
    else:
        # 캐시가 있는 경우에도 최신 재무 지표는 실시간으로 반영
        raw_data = analyzer.load_data(ticker)
        metrics = analyzer.calculate_metrics(raw_data, ticker)

    # Pydantic 모델에 맞춰 데이터 정제 후 반환
    # metrics 딕셔너리의 값을 DividendMetrics 모델로 변환합니다.
    metrics_data = DividendMetrics(
        ticker=ticker,
        cagr_5y=metrics['cagr_5y'],
        consecutive_years=metrics['consecutive_years'],
        last_full_year_div=metrics['last_full_year_div'],
        payout_ratio=metrics.get('payout_ratio'),
        total_return_1y=metrics.get('total_return_1y'),
        ex_dividend_date=metrics.get('ex_dividend_date')
    )
    
    return AnalysisResponse(
        ticker=ticker,
        financial_metrics=metrics_data,
        ai_insight=ai_insight,
        source=source
    )

if __name__ == "__main__":
    import uvicorn
    # 서버 실행 (포트 8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)