# app/main.py

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import engine

from app.config import settings

# 프로젝트 경로 추가
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # catvton_api 절대경로
sys.path.append(os.path.join(BASE_DIR, "vton"))

# 데이터베이스 초기화

models.Base.metadata.create_all(bind=engine)  # 테이블 자동 생성


# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,    # 쿠키/세션/인증 헤더를 쓸 때만 True
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
from app.routes import upload, tryon, result
app.include_router(upload.router)
app.include_router(tryon.router)
app.include_router(result.router)