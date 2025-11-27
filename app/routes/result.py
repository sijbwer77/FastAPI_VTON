# app/routes/result.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.database import get_db
from app.services.result_service import ResultService
from app.repositories.result_repository import ResultRepository
from app.repositories.image_repository import ImageRepository
from app.utils.security import get_current_user
from app import models

router = APIRouter(prefix="/results", tags=["results"])

# Dependency for ResultService
def get_result_service(db: Session = Depends(get_db)) -> ResultService:
    result_repo = ResultRepository(db)
    image_repo = ImageRepository(db)
    return ResultService(result_repo, image_repo)

# 개별 이미지 (Redirect to Supabase)
@router.get("/image/{filename}")
def get_result_image(filename: str, service: ResultService = Depends(get_result_service)):
    url = service.image_repo.get_public_url("result_photo", filename)
    if not url:
        raise HTTPException(status_code=404, detail="Image not found")
    return RedirectResponse(url)

# 모든 결과 리스트 조회
@router.get("/{user_id}")
async def list_results(
    user_id: int,
    result_service: ResultService = Depends(get_result_service),
    current_user: models.User = Depends(get_current_user)
):
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view these results")
        
    return result_service.get_user_results(user_id)
