# app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os, uuid
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from datetime import datetime
from PIL import Image

#라우터 기본 설정
router = APIRouter(prefix="/upload", tags=["upload"])

#디렉토리 설정
PERSON_DIR = './resources/persons' # 전신 사진 저장 위치
CLOTH_DIR = './resources/cloths' # 옷 사진 저장 위치
#폴더 없으면 생성
os.makedirs(PERSON_DIR, exist_ok=True)
os.makedirs(CLOTH_DIR, exist_ok=True) 

# 전신 사진 업로드
@router.post('/person') # /upload/person
async def upload_person( # 비동기 엔드포인트
    file: UploadFile = File(...), # UploadFile 설명: .filename .content_type .read() 사용가능
    db: Session = Depends(get_db), #db 세션 주입이라는데 좀더 공부 필요
):
    if not file.filename.lower().endswith(('.jpg','.jpeg','.png')):
        raise HTTPException(status_code=400, detail='jpg, jepg, png 만 가능합니다')
    
    ext = os.path.splitext(file.filename)[1].lower()
    save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(PERSON_DIR, save_name)

    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    # 이미지 유효성 검사
    try:
        img = Image.open(save_path)
        img.load()
    except Exception:
        os.remove(save_path)
        raise HTTPException(status_code=400, detail="손상된 이미지입니다.")

    new_photo = models.PersonPhoto(
        user_id=1,  # TODO: OAuth 붙이면 가져오기 - 수정필요함
        filename_original=file.filename,
        filename=save_name,
        uploaded_at=datetime.utcnow(),
    )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)

    return {"id": new_photo.id, "filename": save_name}

# 옷 사진 업로드
@router.post("/cloth")
async def upload_cloth(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="jpg, jpeg, png만 가능합니다")

    ext = os.path.splitext(file.filename)[1].lower()
    save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(CLOTH_DIR, save_name)

    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    try:
        Image.open(save_path).verify()
    except Exception:
        os.remove(save_path)
        raise HTTPException(status_code=400, detail="손상된 이미지입니다.")

    new_cloth = models.ClothPhoto(
        user_id=1,  # TODO: OAuth 연결하면 변경
        filename_original=file.filename,
        filename=save_name,
        fitting_type="upper",  # TODO: 나중에 자동/선택 로직
        uploaded_at=datetime.utcnow(),
    )
    db.add(new_cloth)
    db.commit()
    db.refresh(new_cloth)

    return {"id": new_cloth.id, "filename": save_name}
