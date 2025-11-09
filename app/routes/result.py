# app/routes/result.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os
from app import models
from app.database import get_db

router = APIRouter(prefix="/results", tags=["results"])

# 개별 이미지
@router.get("/image/{filename}")
def get_result_image(filename: str):
    file_path = os.path.join("resources/results", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다.")

    return FileResponse(file_path)

# 모든 결과 리스트 조회
@router.get("/{user_id}")
def list_results(user_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(models.ResultPhoto)
        .filter(models.ResultPhoto.user_id == user_id)
        .order_by(models.ResultPhoto.created_at.desc())
        .all()
    )

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
