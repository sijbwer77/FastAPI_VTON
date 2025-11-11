# app/routes/tryon.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services.tryon_service import TryonService, PhotoNotFoundError, VtonProcessingError
from app.repositories.photo_repository import PhotoRepository
from app.repositories.result_repository import ResultRepository

router = APIRouter(prefix="/tryon", tags=["tryon"])

# Dependency for TryonService
def get_tryon_service(db: Session = Depends(get_db)) -> TryonService:
    photo_repo = PhotoRepository(db)
    result_repo = ResultRepository(db)
    return TryonService(photo_repo, result_repo)

class TryonRequest(BaseModel):
    user_id: int
    person_photo_id: int
    cloth_photo_id: int

@router.post("/")
def tryon(req: TryonRequest, tryon_service: TryonService = Depends(get_tryon_service)):
    try:
        result = tryon_service.create_tryon_result(
            user_id=req.user_id,
            person_photo_id=req.person_photo_id,
            cloth_photo_id=req.cloth_photo_id,
        )
        return {
            "message": "합성 완료",
            "result_id": result.id,
            "result_filename": result.filename,
            "result_url": f"/results/image/{result.filename}"
        }
    except PhotoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except VtonProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가상 피팅 처리 중 오류 발생: {e}")
