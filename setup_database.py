
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(
    DATABASE_URL,
    sslmode='require'
)

cur = conn.cursor()

# schema.sql 읽기
with open("database.sql", "r", encoding="utf-8") as f:
    sql = f.read()

# 실행
cur.execute(sql)

conn.commit()

cur.close()
conn.close()

print("Database Setup Complete!")

