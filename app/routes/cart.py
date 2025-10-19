from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.database import get_db

router = APIRouter(prefix="/cart", tags=["cart"])

# 장바구니 조회 (상품 정보 + 수량 포함)
@router.get("/{user_id}")
def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart_items = (
        db.query(models.Cart)
        .filter(models.Cart.user_id == user_id)
        .all()
    )
    return [
        {
            "cart_id": item.id,
            "quantity": item.quantity,  # ✅ 수량 포함
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                "fitting_type": item.product.fitting_type,
                "image_filename": item.product.image_filename,
            },
        }
        for item in cart_items
    ]

# 장바구니 추가 (이미 있으면 수량 +1)
@router.post("/{user_id}/add/{product_id}")
def add_to_cart(user_id: int, product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    cart_item = db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.cloth_id == product_id
    ).first()

    if cart_item:
        cart_item.quantity += 1  # ✅ 수량 증가
        db.commit()
        db.refresh(cart_item)
        return {
            "message": "장바구니 수량이 증가했습니다.",
            "cart_item": {
                "id": cart_item.id,
                "user_id": cart_item.user_id,
                "product_id": cart_item.cloth_id,
                "quantity": cart_item.quantity,
            },
        }

    # 새 항목 추가
    new_item = models.Cart(user_id=user_id, cloth_id=product_id, quantity=1)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {
        "message": "장바구니에 상품이 추가되었습니다.",
        "cart_item": {
            "id": new_item.id,
            "user_id": new_item.user_id,
            "product_id": new_item.cloth_id,
            "quantity": new_item.quantity,
        },
    }

# 장바구니 삭제
@router.delete("/{user_id}/remove/{cart_id}")
def remove_from_cart(user_id: int, cart_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(models.Cart).filter(
        models.Cart.id == cart_id, models.Cart.user_id == user_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="장바구니 항목을 찾을 수 없습니다.")

    db.delete(cart_item)
    db.commit()
    return {"message": "장바구니에서 삭제되었습니다."}
