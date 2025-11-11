# app/routes/result.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os
from app.config import settings
from app.database import get_db
from app.services.result_service import ResultService
from app.repositories.result_repository import ResultRepository

router = APIRouter(prefix="/results", tags=["results"])

# Dependency for ResultService
def get_result_service(db: Session = Depends(get_db)) -> ResultService:
    result_repo = ResultRepository(db)
    return ResultService(result_repo)

# 개별 이미지
@router.get("/image/{filename}")
def get_result_image(filename: str):
    file_path = os.path.join(settings.RESULT_RESOURCE_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다.")

    return FileResponse(file_path)

# 모든 결과 리스트 조회
@router.get("/{user_id}")
def list_results(user_id: int, result_service: ResultService = Depends(get_result_service)):
    results = result_service.get_user_results(user_id)

    return [
        {
            "id": result.id,
            "filename": result.filename,
            "person_photo_id": result.person_photo_id,
            "cloth_photo_id": result.cloth_photo_id,
            "created_at": result.created_at,
            "image_url": f"/results/image/{result.filename}",
        }
        for result in results
    ]
