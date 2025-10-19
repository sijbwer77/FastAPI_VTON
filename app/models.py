from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # ForeignKey("users.id") 로 나중에 확장 가능
    filename_original = Column(String, nullable=False)
    filename = Column(String, unique=True, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)             # 이름 (파일명 기반 자동 생성됨)
    price = Column(Integer, nullable=False)           # 가격
    fitting_type = Column(String, nullable=False)     # 피팅 구분 ("upper", "lower", "overall","etc") -> 합성 시 필요한 정보
    image_filename = Column(String, unique=True, nullable=False)  # cloths 폴더 안의 파일명
    tryon_available = Column(Boolean, default=True)   # 가상 피팅 지원 여부
    created_at = Column(DateTime, default=datetime.utcnow)

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cloth_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    # Product 모델과 관계 설정
    product = relationship("Product", backref="cart_items")

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    photo_id = Column(Integer, ForeignKey("photos.id"))
    cloth_id = Column(Integer, ForeignKey("products.id"))
    result_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

