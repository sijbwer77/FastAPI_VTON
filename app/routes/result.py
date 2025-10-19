# routes/result.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os
from app import models
from app.database import get_db

router = APIRouter(prefix="/results", tags=["results"])

# 🔹 특정 결과 1개 조회 (이미지 파일 반환)
@router.get("/{user_id}/{result_id}")
def get_result(user_id: int, result_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Result).filter_by(id=result_id, user_id=user_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")

    # DB에는 파일명만 저장 (예: abc123_result.png)
    file_path = os.path.join("resources/results", result.result_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"파일이 없습니다: {file_path}")

    return FileResponse(file_path)


# 🔹 유저의 모든 결과 리스트 조회 (JSON, 이미지 URL 포함)
@router.get("/{user_id}")
def list_results(user_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(models.Result)
        .filter(models.Result.user_id == user_id)
        .order_by(models.Result.created_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "photo_id": r.photo_id,
            "cloth_id": r.cloth_id,
            # 프론트에서 바로 <img src>로 쓸 수 있도록 API URL 반환
            "image_url": f"/results/{user_id}/{r.id}",
            "created_at": r.created_at,
        }
        for r in results
    ]
