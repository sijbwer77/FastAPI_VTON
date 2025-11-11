# app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os
from app.services.upload_service import UploadService, InvalidImageFileError, ImageProcessingError
from app.repositories.upload_repository import UploadRepository
from app.database import get_db
from sqlalchemy.orm import Session
from app.utils.security import get_current_user
from app import models

#라우터 기본 설정
router = APIRouter(prefix="/upload", tags=["upload"])

# Dependency for UploadService
def get_upload_service(db: Session = Depends(get_db)) -> UploadService:
    upload_repo = UploadRepository(db)
    return UploadService(upload_repo)

# 전신 사진 업로드
@router.post('/person') # /upload/person
async def upload_person( # 비동기 엔드포인트
    file: UploadFile = File(...), # UploadFile 설명: .filename .content_type .read() 사용가능
    upload_service: UploadService = Depends(get_upload_service),
    current_user: models.User = Depends(get_current_user)
):
    try:
        new_photo = await upload_service.upload_person_photo(file=file, user_id=current_user.id)
        return {"id": new_photo.id, "filename": new_photo.filename}
    except InvalidImageFileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류 발생: {e}")

# 옷 사진 업로드
@router.post("/cloth")
async def upload_cloth(
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(get_upload_service),
    current_user: models.User = Depends(get_current_user)
):
    try:
        new_cloth = await upload_service.upload_cloth_photo(file=file, user_id=current_user.id, fitting_type="upper") # TODO: 나중에 자동/선택 로직
        return {"id": new_cloth.id, "filename": new_cloth.filename}
    except InvalidImageFileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류 발생: {e}")
