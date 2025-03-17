from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from schemas import ProductCreate, CartItemBase, CartCreate, OrderCreate
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
    return {
        "user_id": str(db_cart.user_id) if db_cart.user_id else None,
        "id": str(db_cart.id),
        "items": [],
        "total": 0.0,
        "status": db_cart.status if db_cart.status else "active"
    }

def add_to_cart(db: Session, cart_id: UUID, cart_item: CartItemBase):
    try:
        cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
        if not cart or cart.status != "active":
            return None
        product = db.query(models.Product).filter(models.Product.id == cart_item.product_id).first()
        if not product or product.stock < cart_item.quantity:
            return None
        db_item = models.CartItem(cart_id=cart_id, **cart_item.dict())
        db.add(db_item)
        db.commit()
        updated_cart = db.query(models.Cart).options(
            joinedload(models.Cart.items).joinedload(models.CartItem.product)
        ).filter(models.Cart.id == cart_id).first()
        total = sum(item.quantity * (item.product.price if item.product else 0) for item in updated_cart.items)
        return {
            "user_id": str(updated_cart.user_id) if updated_cart.user_id else None,
            "id": str(updated_cart.id),
            "items": [
                {
                    "product_id": str(item.product.id),
                    "name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.product.price)
                } for item in updated_cart.items if item.product
            ],
            "total": float(total),
            "status": updated_cart.status if updated_cart.status else "active"
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while adding to cart: {str(e)}")

def get_cart(db: Session, cart_id: UUID):
    try:
        cart = db.query(models.Cart).options(
            joinedload(models.Cart.items).joinedload(models.CartItem.product)
        ).filter(models.Cart.id == cart_id).first()

        if not cart:
            return {
                "user_id": None,
                "id": str(cart_id),
                "items": [],
                "total": 0.0,
                "status": "active"
            }

        total = sum(item.quantity * (item.product.price if item.product else 0) for item in cart.items)

        return {
            "user_id": str(cart.user_id) if cart.user_id else None,
            "id": str(cart.id),
            "items": [
                {
                    "product_id": str(item.product.id),
                    "name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.product.price)
                } for item in cart.items if item.product
            ],
            "total": float(total),
            "status": cart.status if cart.status else "active"
        }
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching cart: {str(e)}")

def remove_from_cart(db: Session, cart_id: UUID, product_id: UUID):
    try:
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
        updated_cart = db.query(models.Cart).options(
            joinedload(models.Cart.items).joinedload(models.CartItem.product)
        ).filter(models.Cart.id == cart_id).first()
        if not updated_cart:
            return {
                "user_id": None,
                "id": str(cart_id),
                "items": [],
                "total": 0.0,
                "status": "active"
            }
        total = sum(item.quantity * (item.product.price if item.product else 0) for item in updated_cart.items)
        return {
            "user_id": str(updated_cart.user_id) if updated_cart.user_id else None,
            "id": str(updated_cart.id),
            "items": [
                {
                    "product_id": str(item.product.id),
                    "name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.product.price)
                } for item in updated_cart.items if item.product
            ],
            "total": float(total),
            "status": updated_cart.status if updated_cart.status else "active"
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while removing from cart: {str(e)}")

def create_order(db: Session, order: OrderCreate):
    try:
        cart = db.query(models.Cart).options(
            joinedload(models.Cart.items).joinedload(models.CartItem.product)
        ).filter(models.Cart.id == order.cart_id).first()
        if not cart or cart.status != "active":
            return None
        if not cart.items:
            return None
        total = sum(item.quantity * (item.product.price if item.product else 0) for item in cart.items)
        for item in cart.items:
            product = item.product
            if not product:
                raise ValueError(f"Product not found for cart item {item.id}")
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
        return {
            "id": str(db_order.id),
            "user_id": str(db_order.user_id),
            "cart_id": str(db_order.cart_id),
            "shipping_address": db_order.shipping_address,
            "billing_address": db_order.billing_address,
            "payment_method": db_order.payment_method,
            "status": db_order.status if db_order.status else "pending",
            "total": float(db_order.total)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating order: {str(e)}")

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return [
        {
            "id": str(order.id),
            "user_id": str(order.user_id),
            "cart_id": str(order.cart_id),
            "shipping_address": order.shipping_address,
            "billing_address": order.billing_address,
            "payment_method": order.payment_method,
            "status": order.status if order.status else "pending",
            "total": float(order.total)
        } for order in orders
    ]

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    try:
        categories = db.query(models.Category).offset(skip).limit(limit).all()
        return categories
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching categories: {str(e)}")