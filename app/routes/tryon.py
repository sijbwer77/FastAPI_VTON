# app/routes/tryon.py
import os, uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from vton.run_vton import run_vton # 메인 합성 파트

router = APIRouter(prefix="/tryon", tags=["tryon"])

RESULTS_DIR = "./resources/results"
os.makedirs(RESULTS_DIR, exist_ok=True)


@router.post("/{user_id}/cart/{product_id}")
def tryon(user_id: int, product_id: int, db: Session = Depends(get_db)):
    """
    특정 유저가 업로드한 사진 + 장바구니에 담은 상품으로 합성 실행
    """
    # 1. 유저 사진 가져오기 (지금은 가장 최근 업로드한 사진 사용)
    photo = (
        db.query(models.Photo)
        .filter(models.Photo.user_id == user_id)
        .order_by(models.Photo.uploaded_at.desc())
        .first()
    )
    if not photo:
        raise HTTPException(status_code=404, detail="사용자 사진을 찾을 수 없습니다.")

    # 2. 상품 가져오기
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    # 3. 경로 준비
    user_photo_path = f"./resources/persons/{photo.filename}"
    cloth_path = f"./resources/cloths/{product.image_filename}"
    result_filename = f"{uuid.uuid4().hex}_result.png"
    result_path = os.path.join(RESULTS_DIR, result_filename)

    # 4. 합성 실행
    try:
        run_vton(
            person_path=user_photo_path,
            cloth_path=cloth_path,
            result_path=result_path,
            cloth_type=product.fitting_type,  # upper/lower/overall
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"합성 실패: {e}")

    # 5. DB 저장
    new_result = models.Result(
        user_id=user_id,
        photo_id=photo.id,
        cloth_id=product.id,
        result_path=result_filename,  # 상대 경로만 저장
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)

    return {
        "message": "합성이 완료되었습니다.",
        "result": {
            "id": new_result.id,
            "user_id": new_result.user_id,
            "photo_id": new_result.photo_id,
            "cloth_id": new_result.cloth_id,
            "result_path": new_result.result_path,
        },
    }
