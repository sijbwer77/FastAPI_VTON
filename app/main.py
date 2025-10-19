import sys, os

# 프로젝트 루트(catvton_api) 기준으로 vton 경로 추가
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # catvton_api 절대경로
sys.path.append(os.path.join(BASE_DIR, "vton"))


# app/main.py
from fastapi import FastAPI
from app import models
from app.database import engine

models.Base.metadata.create_all(bind=engine)  # 테이블 자동 생성

app = FastAPI()

# 라우터 추가
from app.routes import upload, tryon, cart, result
app.include_router(upload.router)
app.include_router(tryon.router)
app.include_router(cart.router)
app.include_router(result.router)
