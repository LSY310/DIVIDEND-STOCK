import pandas as pd
from src.database import get_engine

engine = get_engine()

# SQL 쿼리로 데이터 읽어오기
query = "SELECT * FROM dividend_history LIMIT 10;"
df = pd.read_sql(query, engine)

print(df)