import uuid, os
from app.config import settings
from app.repositories.photo_repository import PhotoRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.image_repository import ImageRepository
from app.repositories.upload_repository import UploadRepository
from app.services import vton_service
from app import models, schemas # For type hinting the return value

# Custom Exceptions
class PhotoNotFoundError(Exception):
    pass

class VtonProcessingError(Exception):
    pass

class TryonService:
    def __init__(self, 
                 photo_repo: PhotoRepository, 
                 result_repo: ResultRepository,
                 image_repo: ImageRepository,
                 upload_repo: UploadRepository):
        self.photo_repo = photo_repo
        self.result_repo = result_repo
        self.image_repo = image_repo
        self.upload_repo = upload_repo

    def _get_mime_type(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            return 'image/jpeg'
        elif ext == '.png':
            return 'image/png'
        elif ext == '.webp':
            return 'image/webp'
        else:
            return 'image/png' # Default

    def create_tryon_result(self, user_id: int, person_photo_id: int, cloth_photo_id: int) -> schemas.Photo:
        person_photo = self.photo_repo.get_person_photo_by_id(person_photo_id, user_id)
        if not person_photo:
            raise PhotoNotFoundError("선택한 사람 사진을 찾을 수 없습니다.")

        cloth_photo = self.photo_repo.get_cloth_photo_by_id(cloth_photo_id)
        if not cloth_photo:
            raise PhotoNotFoundError("선택한 옷 사진을 찾을 수 없습니다.")

        # 3) Supabase에서 이미지 다운로드
        try:
            person_image_bytes = self.image_repo.download_image("person_photo", person_photo.filename)
            cloth_image_bytes = self.image_repo.download_image("cloth_photo", cloth_photo.filename)
        except Exception as e:
            raise VtonProcessingError(f"이미지 다운로드 실패: {e}")

        # 4) VTON 실행
        try:
            if settings.VTON_METHOD == "vertex_ai":
                result_image_bytes = vton_service.run_vton(
                    person_image_bytes=person_image_bytes,
                    person_mime_type=self._get_mime_type(person_photo.filename),
                    cloth_image_bytes=cloth_image_bytes,
                    cloth_mime_type=self._get_mime_type(cloth_photo.filename),
                    cloth_type=cloth_photo.fitting_type,
                )
            else:
                raise Exception("vertex_ai 환경 변수 설정이 필요합니다")
            
            if not result_image_bytes:
                 raise VtonProcessingError("합성 결과 이미지가 생성되지 않았습니다.")

        except Exception as e:
            raise VtonProcessingError(f"합성 실패: {e}")

        # 5) 결과 업로드 및 DB 저장
        result_filename = f"{uuid.uuid4().hex}_result.png"
        try:
            self.upload_repo.upload_file(
                bucket="result_photo",
                path=result_filename,
                file_content=result_image_bytes,
                content_type="image/png"
            )
        except Exception as e:
            raise VtonProcessingError(f"결과 이미지 업로드 실패: {e}")

        new_result = self.result_repo.create_result(
            user_id=user_id,
            person_photo_id=person_photo_id,
            cloth_photo_id=cloth_photo_id,
            filename=result_filename,
        )
        return new_result