import os
from sqlalchemy.orm import Session
from app import models, schemas
from app.repositories.user_repository import UserRepository
from app.repositories.image_repository import ImageRepository, CATEGORY_DIRS
from typing import List, Optional, Type

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    모든 사용자 목록을 가져오는 서비스 함수입니다.
    """
    user_repo = UserRepository(db)
    return user_repo.get_all_users(skip=skip, limit=limit)

def update_user(db: Session, user_id: int, user_update: schemas.AdminUserUpdate) -> models.User | None:
    """
    사용자 정보를 업데이트하는 서비스 함수입니다.
    """
    user_repo = UserRepository(db)
    updated_user = user_repo.update_user_details(user_id=user_id, user_update=user_update)
    return updated_user

# --- Photo Management Services ---

def get_all_photos(db: Session, category: str) -> Optional[List[Type[models.Base]]]:
    """
    카테고리별 모든 사진 레코드를 가져오는 서비스 함수입니다.
    """
    image_repo = ImageRepository(db)
    return image_repo.get_all_photos_by_category(category)

def delete_photo(db: Session, category: str, photo_id: int) -> bool:
    """
    사진을 DB와 파일 시스템에서 모두 삭제하는 서비스 함수입니다.
    """
    image_repo = ImageRepository(db)
    
    # 1. DB에서 레코드 삭제 시도 및 삭제된 객체 정보 가져오기
    deleted_photo_record = image_repo.delete_photo_by_id(category, photo_id)
    
    if not deleted_photo_record:
        return False # DB에서 해당 사진을 찾지 못함

    # 2. 파일 시스템에서 실제 파일 삭제
    try:
        directory = CATEGORY_DIRS.get(category)
        if directory:
            file_path = os.path.join(directory, deleted_photo_record.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                # DB에는 있었지만 파일이 없는 경우, 일단 성공으로 간주
                pass
        return True
    except Exception as e:
        # 파일 삭제 실패 시 로깅 (DB는 이미 롤백되었거나 커밋됨)
        # 이 경우 수동 개입이 필요할 수 있음을 알려야 할 수도 있음
        print(f"Error deleting file for photo ID {photo_id}: {e}")
        # 파일 삭제에 실패했더라도 DB 레코드는 삭제되었으므로 True를 반환할 수 있음
        # 또는 False를 반환하고 트랜잭션을 롤백하는 더 복잡한 로직을 구현할 수도 있음
        return True

def delete_user_account(db: Session, user_id: int) -> bool:
    """
    사용자 계정과 관련된 모든 데이터(파일, DB 레코드)를 삭제합니다.
    """
    user_repo = UserRepository(db)
    image_repo = ImageRepository(db)

    # 1. 사용자가 존재하는지 확인
    user_to_delete = user_repo.get_by_id(user_id)
    if not user_to_delete:
        return False

    # 2. 사용자와 관련된 모든 사진 파일 삭제
    all_photos = image_repo.get_all_photos_for_user(user_id)
    for category, photo_list in all_photos.items():
        directory = CATEGORY_DIRS.get(category)
        if not directory:
            continue
        for photo in photo_list:
            try:
                file_path = os.path.join(directory, photo.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                # 파일 삭제 실패 시 로깅. DB 삭제는 계속 진행합니다.
                print(f"Error deleting file {file_path}: {e}")

    # 3. 사용자 레코드 삭제
    # DB 스키마에서 ondelete='CASCADE'가 설정되어 있다고 가정합니다.
    # User를 삭제하면 관련된 person_photos, cloth_photos, result_photos가 자동으로 삭제됩니다.
    # 만약 CASCADE 설정이 없다면, 각 사진 레코드를 여기서 수동으로 삭제해야 합니다.
    user_repo.delete_user(user_id)
    
    return True
