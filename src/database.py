import psycopg2
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
    # 데이터를 담을 테이블 만들기
    query = """
    CREATE TABLE IF NOT EXISTS dividend_history (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10),
        date TIMESTAMP,
        dividend FLOAT,
        UNIQUE(ticker, date) -- 중복 데이터 방지
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
    print("✅ DB 테이블 생성 완료!")