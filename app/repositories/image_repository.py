import os
import logging
from typing import List, Optional

from app.database import SessionLocal
from app.models import PersonPhoto, ClothPhoto, ResultPhoto

# 카테고리 이름과 실제 디렉토리를 매핑합니다.
CATEGORY_DIRS = {
    "clothes": "resources/cloths",
    "persons": "resources/persons",
    "results": "resources/results",
}

# 카테고리 이름과 ORM 모델을 매핑합니다.
CATEGORY_MODELS = {
    "clothes": ClothPhoto,
    "persons": PersonPhoto,
    "results": ResultPhoto,
}

def list_images(category: str) -> Optional[List[str]]:
    """
    지정된 카테고리에 대해 데이터베이스를 쿼리하여 이미지 파일 목록을 가져옵니다.
    카테고리가 유효하지 않으면 None을 반환합니다.
    """
    model = CATEGORY_MODELS.get(category)
    if not model:
        logging.error(f"Invalid image category requested: {category}")
        return None

    db = SessionLocal()
    try:
        # 데이터베이스에서 filename 목록을 조회합니다.
        image_records = db.query(model.filename).all()
        # SQLAlchemy의 결과는 튜플 리스트이므로, 각 튜플의 첫 번째 요소를 추출합니다.
        image_files = [record[0] for record in image_records]
        return image_files
    except Exception as e:
        logging.error(f"Error querying database for category {category}: {e}")
        return []
    finally:
        db.close()

def get_image_path(category: str, image_name: str) -> Optional[str]:
    """
    DB를 확인하여 카테고리와 이미지 이름이 유효한지 검증하고,
    유효하다면 전체 파일 경로를 반환합니다.
    """
    target_dir = CATEGORY_DIRS.get(category)
    model = CATEGORY_MODELS.get(category)
    if not target_dir or not model:
        return None

    # 경로 조작 공격 방지를 위한 보안 검사
    if ".." in image_name or "/" in image_name or "\\" in image_name:
        logging.warning(f"Invalid image name requested: {image_name}")
        return None

    db = SessionLocal()
    try:
        # 데이터베이스에 해당 파일 이름의 레코드가 있는지 확인합니다.
        record_exists = db.query(model).filter(model.filename == image_name).first()
        if not record_exists:
            return None
    except Exception as e:
        logging.error(f"Error querying database for image {image_name} in category {category}: {e}")
        return None
    finally:
        db.close()

    # 레코드가 존재하면, 파일 시스템 경로를 조합하여 반환합니다.
    image_path = os.path.join(target_dir, image_name)

    # DB에 레코드는 있지만 실제 파일이 없을 경우를 대비한 추가 검사
    if not os.path.isfile(image_path):
        logging.warning(f"DB record exists for {image_path}, but the file is missing.")
        return None
    
    return image_path
