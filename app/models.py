# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=False) #구글 OAuth 로그인
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    profile_image = Column(String, nullable=True) # google 프로필 이미지 URL
    is_active = Column(Boolean, default = True)
    is_superuser = Column(Boolean, default = False)
    created_at = Column(DateTime, default=datetime.utcnow)

    person_photos = relationship("PersonPhoto", back_populates="user")
    cloth_photos = relationship("ClothPhoto", back_populates="user")
    result_photos = relationship("ResultPhoto", back_populates="user")


class PersonPhoto(Base): # 사람 사진 저장
    __tablename__ = "person_photos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename_original = Column(String, nullable=False)
    filename = Column(String, unique=True, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="person_photos")
    result_photos = relationship("ResultPhoto", back_populates="person_photo")

class ClothPhoto(Base): # 옷 사진 저장
    __tablename__ = "cloth_photos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename_original = Column(String, nullable=False)
    filename = Column(String, unique=True, nullable=False)
    fitting_type = Column(String, nullable=False, default='upper')
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cloth_photos")
    result_photos = relationship("ResultPhoto", back_populates="cloth_photo")


class ResultPhoto(Base): # 결과 저장
    __tablename__ = "result_photos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    person_photo_id = Column(Integer, ForeignKey("person_photos.id"), nullable=False)
    cloth_photo_id = Column(Integer, ForeignKey("cloth_photos.id"), nullable =False)
    filename = Column(String,unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="result_photos")
    person_photo = relationship("PersonPhoto", back_populates="result_photos")
    cloth_photo = relationship("ClothPhoto", back_populates="result_photos")

