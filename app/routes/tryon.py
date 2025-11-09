# app/routes/tryon.py
import os, uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import models
from app.database import get_db
from vton.run_vton import run_vton

router = APIRouter(prefix="/tryon", tags=["tryon"])

RESULTS_DIR = "./resources/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

class TryonRequest(BaseModel):
    user_id: int
    person_photo_id: int
    cloth_photo_id: int


@router.post("/")
def tryon(req: TryonRequest, db: Session = Depends(get_db)):

    # 1) 유저 전신 사진 조회
    person_photo = db.query(models.PersonPhoto).filter(
        models.PersonPhoto.id == req.person_photo_id,
        models.PersonPhoto.user_id == req.user_id
    ).first()

    if not person_photo:
        raise HTTPException(status_code=404, detail="선택한 사람 사진을 찾을 수 없습니다.")

    # 2) 유저 옷 사진 조회
    cloth_photo = db.query(models.ClothPhoto).filter(
        models.ClothPhoto.id == req.cloth_photo_id,
        models.ClothPhoto.user_id == req.user_id
    ).first()

    if not cloth_photo:
        raise HTTPException(status_code=404, detail="선택한 옷 사진을 찾을 수 없습니다.")

    # 3) 파일 경로 생성
    person_path = f"./resources/persons/{person_photo.filename}"
    cloth_path = f"./resources/cloths/{cloth_photo.filename}"

    if not os.path.exists(person_path):
        raise HTTPException(status_code=500, detail="사람 이미지 파일이 존재하지 않습니다.")

    if not os.path.exists(cloth_path):
        raise HTTPException(status_code=500, detail="옷 이미지 파일이 존재하지 않습니다.")

    result_filename = f"{uuid.uuid4().hex}_result.png"
    result_path = f"{RESULTS_DIR}/{result_filename}"

    # 4) VTON 실행
    try:
        run_vton(
            person_path=person_path,
            cloth_path=cloth_path,
            result_path=result_path,
            cloth_type=cloth_photo.fitting_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"합성 실패: {e}")

    # 5) DB 저장
    result = models.ResultPhoto(
        user_id=req.user_id,
        person_photo_id=req.person_photo_id,
        cloth_photo_id=req.cloth_photo_id,
        filename=result_filename,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return {
        "message": "합성 완료",
        "result_id": result.id,
        "result_filename": result.filename,
        "result_url": f"/results/{result.filename}"
    }
