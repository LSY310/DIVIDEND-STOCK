# API가 주고받는 데이터의 형식을 정의 Pydantic을 쓰면 타입 체크가 자동화되어 안전
from pydantic import BaseModel, Field
from typing import Optional

# 금융 지표를 담는 모델
class DividendMetrics(BaseModel):
    ticker: str
    cagr_5y: float | str = Field(..., description="5년 연평균 성장률")
    consecutive_years: int = Field(..., description="연속 배당 성장 연수")
    last_full_year_div: float = Field(..., description="직전 연도 총 배당금")
    payout_ratio: Optional[float] = Field(None, description="배당 성향 (%)")
    total_return_1y: Optional[float] = Field(None, description="1년 총 수익률 (%)")
    ex_dividend_date: Optional[str] = Field(None, description="최근 배당락일 (YYYY-MM-DD)")

# API 최종 응답 형식을 정의하는 모델(지표 + AI 분석글 + 데이터 출처)
class AnalysisResponse(BaseModel):
    ticker: str
    financial_metrics: DividendMetrics
    ai_insight: str
    source: str = Field(..., description="데이터 출처 (api 또는 cache)")