from sqlalchemy.orm import Session
from models import Product, CartItem, Order
from schemas import ProductCreate, CartItemBase, OrderCreate

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session):
    return db.query(Product).all()

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def add_to_cart(db: Session, cart_item: CartItemBase, user_id: int):
    db_item = CartItem(**cart_item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_cart(db: Session, user_id: int):
    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    total = sum(item.quantity * get_product(db, item.product_id).price for item in items)
    return {"items": items, "total": total}

def remove_from_cart(db: Session, product_id: int, user_id: int):
    db.query(CartItem).filter(CartItem.product_id == product_id, CartItem.user_id == user_id).delete()
    db.commit()
    return get_cart(db, user_id)

def create_order(db: Session, order: OrderCreate, user_id: int):
    cart = get_cart(db, user_id)
    db_order = Order(**order.dict(), user_id=user_id, total=cart["total"])
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    return db_order