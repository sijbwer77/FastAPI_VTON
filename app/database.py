from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings # .env 파일에서 값을 읽어온 settings 객체

#아래 주소를 .env 파일 DATABASE_URL에 적어주세요
#DATABASE_URL="postgresql://postgres.lbaqzmqmlbythlozegee:1234@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

# 1. settings 객체에서 DATABASE_URL을 한 번만 읽어옵니다.
engine_args = {}

# 2. DB URL이 SQLite일 때만 connect_args를 추가하도록 처리
if "sqlite" in settings.DATABASE_URL:
    engine_args["connect_args"] = {"check_same_thread": False}

# 3. engine을 한 번만 생성합니다.
engine = create_engine(
    settings.DATABASE_URL, **engine_args
)
# --- (이하 코드는 전혀 수정할 필요 없음) ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 의존성 주입용
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
