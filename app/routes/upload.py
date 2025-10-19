from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os, uuid
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from datetime import datetime
from PIL import Image

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "./resources/persons"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_person(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png are allowed")

    # 파일명: 날짜_UUID.확장자
    ext = os.path.splitext(file.filename)[1].lower()
    save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, save_name)

    # 파일 저장 (read 한 번만!)
    contents = await file.read()
    with open(save_path, "wb") as buffer:
        buffer.write(contents)

    # 저장 후 유효성 검사 (깨진 파일 방지)
    try:
        Image.open(save_path).verify()
    except Exception:
        os.remove(save_path)
        raise HTTPException(status_code=400, detail="올바르지 않은 이미지 파일입니다.")

    # DB 저장
    new_photo = models.Photo(
        user_id=1,
        filename_original=file.filename,
        filename=save_name,
        uploaded_at=datetime.utcnow(),
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)

    return {
        "id": new_photo.id,
        "filename": save_name,
        "uploaded_at": new_photo.uploaded_at,
    }
