import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# resources/cloths/add_all_products.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

CLOTHS = [
    {
        "filename": "Lee_니트_화이트.jpg",
        "fitting_type": "upper",
        "price": 38400,
    },
    {
        "filename": "MONTAUK_반팔티_블랙.jpg",
        "fitting_type": "upper",
        "price": 19900,
    },
]

# 테이블 생성 (없으면 자동 생성)
models.Base.metadata.create_all(bind=engine)

def filename_to_name(filename: str) -> str:
    """파일명을 사람이 읽기 좋은 상품명으로 변환 (확장자 제거, _ → 공백)"""
    import os
    name, _ = os.path.splitext(filename)
    return name.replace("_", " ")

def register_cloths():
    db: Session = SessionLocal()
    try:
        for cloth in CLOTHS:
            exists = db.query(models.Product).filter_by(image_filename=cloth["filename"]).first()
            if exists:
                # 만약 price 나 fitting_type이 바뀌었으면 업데이트
                updated = False
                if exists.fitting_type != cloth["fitting_type"]:
                    exists.fitting_type = cloth["fitting_type"]
                    updated = True
                if exists.price != cloth["price"]:
                    exists.price = cloth["price"]
                    updated = True
                if updated:
                    db.commit()
                    print(
                        f"🔄 업데이트됨: "
                        f"[ID={exists.id}] {exists.name} | "
                        f"가격={exists.price}원 | "
                        f"타입={exists.fitting_type}"
                    )
                else:
                    print(f"⚠️ 이미 등록됨: "
                        f"[ID={exists.id}] {exists.name} | "
                        f"가격={exists.price}원 | "
                        f"타입={exists.fitting_type}"
                    )
                continue

            # 새 상품 추가
            new_product = models.Product(
                name=filename_to_name(cloth["filename"]),
                fitting_type=cloth["fitting_type"],
                price=cloth["price"],
                image_filename=cloth["filename"],
                tryon_available=True,
                created_at=datetime.utcnow(),
            )

            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            print(
                f"✅ 등록 완료: "
                f"[ID={new_product.id}] {new_product.name} | "
                f"가격={new_product.price}원 | "
                f"타입={new_product.fitting_type}"
            )
            
    except Exception as e:
        db.rollback()
        print(f"❌ 오류: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    register_cloths()
