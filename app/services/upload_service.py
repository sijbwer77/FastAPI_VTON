import os, uuid
from datetime import datetime
from PIL import Image
from fastapi import UploadFile, HTTPException
from app.repositories.upload_repository import UploadRepository
from app import models # For type hinting the return value

# Custom Exceptions
class InvalidImageFileError(Exception):
    pass

class ImageProcessingError(Exception):
    pass

class UploadService:
    def __init__(self, upload_repo: UploadRepository):
        self.upload_repo = upload_repo

    async def upload_person_photo(self, file: UploadFile, user_id: int = 1) -> models.PersonPhoto: # TODO: user_id from auth
        if not file.filename.lower().endswith(('.jpg','.jpeg','.png')):
            raise InvalidImageFileError('jpg, jpeg, png 만 가능합니다')

        ext = os.path.splitext(file.filename)[1].lower()
        save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex}{ext}"
        save_path = os.path.join('./resources/persons', save_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True) # Ensure persons directory exists

        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)

        try:
            img = Image.open(save_path)
            img.load()
        except Exception:
            os.remove(save_path)
            raise ImageProcessingError("손상된 이미지입니다.")

        new_photo = self.upload_repo.create_person_photo(
            user_id=user_id,
            filename_original=file.filename,
            filename=save_name,
        )
        return new_photo

    async def upload_cloth_photo(self, file: UploadFile, user_id: int = 1, fitting_type: str = "upper") -> models.ClothPhoto: # TODO: user_id from auth, fitting_type logic
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            raise InvalidImageFileError("jpg, jpeg, png만 가능합니다")

        ext = os.path.splitext(file.filename)[1].lower()
        save_name = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex}{ext}"
        save_path = os.path.join('./resources/cloths', save_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True) # Ensure cloths directory exists

        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)

        try:
            Image.open(save_path).verify()
        except Exception:
            os.remove(save_path)
            raise ImageProcessingError("손상된 이미지입니다.")

        new_cloth = self.upload_repo.create_cloth_photo(
            user_id=user_id,
            filename_original=file.filename,
            filename=save_name,
            fitting_type=fitting_type,
        )
        return new_cloth
