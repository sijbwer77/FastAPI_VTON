import os, uuid
from app.config import settings
from app.repositories.photo_repository import PhotoRepository
from app.repositories.result_repository import ResultRepository
from vton.run_vton import run_vton
from app.services import vton_service
from app import models # For type hinting the return value

# Custom Exceptions
class PhotoNotFoundError(Exception):
    pass

class VtonProcessingError(Exception):
    pass

class TryonService:
    def __init__(self, photo_repo: PhotoRepository, result_repo: ResultRepository):
        self.photo_repo = photo_repo
        self.result_repo = result_repo

    def create_tryon_result(self, user_id: int, person_photo_id: int, cloth_photo_id: int) -> models.ResultPhoto:
        person_photo = self.photo_repo.get_person_photo_by_id(person_photo_id, user_id)
        if not person_photo:
            raise PhotoNotFoundError("선택한 사람 사진을 찾을 수 없습니다.")

        cloth_photo = self.photo_repo.get_cloth_photo_by_id(cloth_photo_id)
        if not cloth_photo:
            raise PhotoNotFoundError("선택한 옷 사진을 찾을 수 없습니다.")

        # 3) 파일 경로 생성
        person_path = os.path.join(settings.PERSON_RESOURCE_DIR, person_photo.filename)
        cloth_path = os.path.join(settings.CLOTH_RESOURCE_DIR, cloth_photo.filename)

        if not os.path.exists(person_path):
            raise VtonProcessingError("사람 이미지 파일이 존재하지 않습니다.")

        if not os.path.exists(cloth_path):
            raise VtonProcessingError("옷 이미지 파일이 존재하지 않습니다.")

        result_filename = f"{uuid.uuid4().hex}_result.png"
        result_path = os.path.join(settings.RESULT_RESOURCE_DIR, result_filename)

        # 4) VTON 실행
        try:
            actual_result_path = None
            if settings.VTON_METHOD == "vertex_ai":
                actual_result_path = vton_service.run_vton(
                    person_path=person_path,
                    cloth_path=cloth_path,
                    cloth_type=cloth_photo.fitting_type,
                )
            else:
                actual_result_path = run_vton(
                    person_path=person_path,
                    cloth_path=cloth_path,
                    result_path=result_path,
                    cloth_type=cloth_photo.fitting_type,
                )
            
            if actual_result_path is None or not os.path.exists(actual_result_path):
                raise VtonProcessingError("합성 결과 파일이 생성되지 않았습니다.")
            
            # 실제 생성된 파일명으로 DB에 저장
            final_filename = os.path.basename(actual_result_path)

        except Exception as e:
            raise VtonProcessingError(f"합성 실패: {e}")

        # 5) DB 저장
        new_result = self.result_repo.create_result(
            user_id=user_id,
            person_photo_id=person_photo_id,
            cloth_photo_id=cloth_photo_id,
            filename=final_filename,
        )
        return new_result
