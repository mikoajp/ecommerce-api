from sqlalchemy.orm import Session, joinedload
from schemas import ProductCreate, CartItemBase, Cart, OrderCreate, Order, CartCreate
import models
from uuid import UUID

def create_product(db: Session, product: ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: UUID):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def create_cart(db: Session, cart: CartCreate):
    db_cart = models.Cart(**cart.dict())
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return {**db_cart.__dict__, "items": [], "total": 0.0}

def add_to_cart(db: Session, cart_id: UUID, cart_item: CartItemBase):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart or cart.status != "active":
        return None
    product = db.query(models.Product).filter(models.Product.id == cart_item.product_id).first()
    if not product or product.stock < cart_item.quantity:
        return None
    db_item = models.CartItem(cart_id=cart_id, **cart_item.dict())
    db.add(db_item)
    db.commit()
    return cart

def get_cart(db: Session, cart_id: UUID):
    cart = db.query(models.Cart).options(joinedload(models.Cart.items)).filter(models.Cart.id == cart_id).first()
    if not cart:
        return None
    total = sum(item.quantity * item.product.price for item in cart.items)
    return {**cart.__dict__, "items": cart.items, "total": total}

def remove_from_cart(db: Session, cart_id: UUID, product_id: UUID):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart or cart.status != "active":
        return None
    item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart_id,
        models.CartItem.product_id == product_id
    ).first()
    if item:
        db.delete(item)
        db.commit()
    return cart

def create_order(db: Session, order: OrderCreate):
    cart = db.query(models.Cart).options(joinedload(models.Cart.items)).filter(models.Cart.id == order.cart_id).first()
    if not cart or cart.status != "active":
        return None
    if not cart.items:
        return None
    total = sum(item.quantity * item.product.price for item in cart.items)
    for item in cart.items:
        product = item.product
        if product.stock < item.quantity:
            raise ValueError(f"Insufficient stock for product {product.name}")
        product.stock -= item.quantity
    db_order = models.Order(
        user_id=cart.user_id,
        cart_id=order.cart_id,
        shipping_address=order.shipping_address,
        billing_address=order.billing_address,
        payment_method=order.payment_method,
        total=total
    )
    cart.status = "completed"
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()