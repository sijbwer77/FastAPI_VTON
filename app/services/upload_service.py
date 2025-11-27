import os, uuid, io
from datetime import datetime
from PIL import Image
from fastapi import UploadFile
from app.repositories.upload_repository import UploadRepository
from app import schemas

# Custom Exceptions
class InvalidImageFileError(Exception):
    pass

class ImageProcessingError(Exception):
    pass

class UploadService:
    def __init__(self, upload_repo: UploadRepository):
        self.upload_repo = upload_repo

    async def upload_person_photo(self, file: UploadFile, user_id: int) -> schemas.Photo:
        if not file.filename.lower().endswith(('.jpg','.jpeg','.png')):
            raise InvalidImageFileError('jpg, jpeg, png 만 가능합니다')

        ext = os.path.splitext(file.filename)[1].lower()
        save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex}{ext}"

        contents = await file.read()

        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception:
            raise ImageProcessingError("손상된 이미지입니다.")

        self.upload_repo.upload_file(
            bucket="person_photo",
            path=save_name,
            file_content=contents,
            content_type=file.content_type
        )

        new_photo = self.upload_repo.create_person_photo(
            user_id=user_id,
            filename_original=file.filename,
            filename=save_name,
        )
        return new_photo

    async def upload_cloth_photo(self, file: UploadFile, user_id: int, fitting_type: str = "upper") -> schemas.Photo:
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
        
        self.upload_repo.upload_file(
            bucket="cloth_photo",
            path=save_name,
            file_content=contents,
            content_type=file.content_type
        )

        new_cloth = self.upload_repo.create_cloth_photo(
            user_id=user_id,
            filename_original=file.filename,
            filename=save_name,
            fitting_type=fitting_type,
        )
        return new_cloth
