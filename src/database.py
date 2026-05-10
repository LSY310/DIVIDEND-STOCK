#PostgreSQL 연결 설정과 프로젝트에 필요한 테이블을 자동으로 생성하는 로직
from sqlalchemy import create_engine,text
import os
from dotenv import load_dotenv

load_dotenv()

# DB 연결 정보
DB_URL = "postgresql://dev_user:dev_password@localhost:5432/dividend_flow"

def get_engine():
    # SQLAlchemy 엔진 생성 (Pandas와 DB를 연결해줌)
    return create_engine(DB_URL)

def create_tables():
    # 배당 이력 저장용과 AI 리포트 캐시용 테이블 생성
    query = """
    CREATE TABLE IF NOT EXISTS dividend_history (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10),
        date TIMESTAMP,
        dividend FLOAT,
        UNIQUE(ticker, date) -- 동일 날짜 중복 데이터 방지
    );

    CREATE TABLE IF NOT EXISTS ai_report_cache (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) UNIQUE,
        report_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    """

    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text(query))  # text(query)로 감싸기
        conn.commit()             # 변경 사항 확정(Commit)

    print("DB 테이블 생성 완료")