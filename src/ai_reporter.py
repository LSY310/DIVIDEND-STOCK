import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AIReporter:
    def __init__(self):
        # Gemini Pro 모델 설정
        self.model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

    async def generate_report(self, metrics: dict):
        prompt = f"""
        당신은 배당 성장주 전문 투자 컨설턴트입니다. 아래 분석 지표를 바탕으로 {metrics['ticker']}에 대한 투자 의견을 작성하세요.

        [분석 지표]
        - 티커: {metrics['ticker']}
        - 5년 평균 배당 성장률(CAGR): {metrics['cagr_5y']}%
        - 연속 배당 성장 연수: {metrics['consecutive_years']}년
        - 최근 연간 배당금: ${metrics['last_full_year_div']}

        [요구 사항]
        1. 배당 성장률이 5% 이상인 경우 긍정적으로, 0% 이하인 경우 보수적으로 평가할 것.
        2. 연속 성장 연수를 근거로 배당의 '신뢰도'를 언급할 것.
        3. 마지막 한 줄은 "매수/보유/관망" 중 하나로 투자 의견을 제시하고 이유를 덧붙일 것.
        
        답변은 한국어로, 전문가답게 작성해 주세요.
        """
        response = await self.model.generate_content_async(prompt)
        return response.text