import os, uuid, io
from datetime import datetime
from supabase import create_client, Client
from PIL import Image
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.repositories.upload_repository import UploadRepository
from app import models, schemas # For type hinting the return value

#DB connection
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Custom Exceptions
class InvalidImageFileError(Exception):
    pass

class ImageProcessingError(Exception):
    pass

class UploadService:
    def __init__(self, upload_repo: UploadRepository):
        self.upload_repo = upload_repo

    async def upload_person_photo(self, file: UploadFile, user_id: int = 1) -> schemas.Photo: # TODO: user_id from auth
        if not file.filename.lower().endswith(('.jpg','.jpeg','.png')):
            raise InvalidImageFileError('jpg, jpeg, png 만 가능합니다')

        ext = os.path.splitext(file.filename)[1].lower()
        save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex}{ext}"

        contents = await file.read()

        try:
            image = Image.open(io.BytesIO(contents))
            image.verify() # 파일이 깨졌는지 확인
        except Exception:
            raise ImageProcessingError("손상된 이미지입니다.")

        try:
            supabase.storage.from_("person_photo").upload(
                path=save_name,
                file=contents,
                file_options={"content-type": file.content_type}
            )
        except Exception as e:
            raise Exception(f"Supabase(person_photo) 업로드 실패: {e}")

        new_photo = self.upload_repo.create_person_photo(
            user_id=user_id,
            filename_original=file.filename,
            filename=save_name,
        )
        return new_photo

    async def upload_cloth_photo(self, file: UploadFile, user_id: int = 1, fitting_type: str = "upper") -> schemas.Photo: # TODO: user_id from auth, fitting_type logic
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            raise InvalidImageFileError("jpg, jpeg, png만 가능합니다")

        ext = os.path.splitext(file.filename)[1].lower()
        save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex}{ext}"

        contents = await file.read()

        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception:
            raise ImageProcessingError("손상된 이미지입니다.")
        
        try:
            supabase.storage.from_("cloth_photo").upload(
            path=save_name,          # 저장될 파일 이름
            file=contents,           # 파일의 실제 데이터
            file_options={"content-type": file.content_type} # 이미지 타입 알려주기 (jpg/png 등)
    )
        except Exception as e:
             raise Exception(f"Supabase 업로드 실패: {e}")



        new_cloth = self.upload_repo.create_cloth_photo(
            user_id=user_id,
            filename_original=file.filename,
            filename=save_name,
            fitting_type=fitting_type,
        )
        return new_cloth
