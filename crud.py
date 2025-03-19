from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

import models
from schemas import ProductCreate, CartItemBase, CartCreate, OrderCreate, UserRegister, Order, UserUpdate, \
    ChangePassword
from models import Product, Cart, CartItem, Order, Category, User, Promotion
from uuid import UUID
from auth import get_password_hash, verify_password
from schemas import Order as OrderSchema
from datetime import datetime

def create_product(db: Session, product: ProductCreate):
    try:
        db_product = Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating product: {str(e)}")

def get_products(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(Product).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching products: {str(e)}")

def get_product(db: Session, product_id: UUID):
    try:
        return db.query(Product).filter(Product.id == product_id).first()
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching product: {str(e)}")

def create_cart(db: Session, cart: CartCreate):
    try:
        db_cart = Cart(**cart.model_dump())
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
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating cart: {str(e)}")

def add_to_cart(db: Session, cart_id: UUID, cart_item: CartItemBase):
    try:
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart or cart.status != "active":
            return None
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if not product or product.stock < cart_item.quantity:
            return None
        db_item = CartItem(cart_id=cart_id, **cart_item.model_dump())
        db.add(db_item)
        db.commit()
        updated_cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == cart_id).first()
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
        cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == cart_id).first()

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
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart or cart.status != "active":
            return None
        item = db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        ).first()
        if item:
            db.delete(item)
            db.commit()
        updated_cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == cart_id).first()
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

def update_cart_item_quantity(db: Session, cart_id: UUID, product_id: UUID, quantity: int):
    try:
        cart = db.query(Cart).filter(Cart.id == cart_id, Cart.status == "active").first()
        if not cart:
            return None
        item = db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        ).first()
        if not item:
            return None
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product or product.stock < quantity:
            return None
        item.quantity = quantity
        db.commit()
        updated_cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == cart_id).first()
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
        raise Exception(f"Database error while updating cart item quantity: {str(e)}")


def validate_promotion(db: Session, code: str) -> Promotion:
    """
    Waliduje kod promocyjny i zwraca obiekt Promotion, jeśli jest ważny.
    """
    promotion = db.query(Promotion).filter(Promotion.code == code).first()
    if not promotion:
        return None
    now = datetime.utcnow()
    if promotion.valid_from > now or promotion.valid_until < now:
        return None
    if promotion.max_uses and promotion.uses >= promotion.max_uses:
        return None
    return promotion


def create_order(db: Session, order: OrderCreate) -> Order | None:
    """
    Tworzy nowe zamówienie na podstawie koszyka z opcjonalnym kodem promocyjnym.
    """
    try:

        cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == order.cart_id).first()

        if not cart or cart.status != "active" or not cart.items:
            return None

        total = sum(item.product.price * item.quantity for item in cart.items)

        for item in cart.items:
            product = item.product
            if not product:
                raise ValueError(f"Produkt nie znaleziony dla elementu koszyka {item.id}")
            if product.stock < item.quantity:
                raise ValueError(f"Niewystarczający stan magazynowy dla produktu {product.name}")
            product.stock -= item.quantity
            db.add(product)

        applied_discount = 0.0
        if order.promotion_code:
            promotion = validate_promotion(db, order.promotion_code)
            if promotion:
                discount = total * (promotion.discount_percentage / 100)
                applied_discount = discount
                total -= discount
                promotion.uses += 1
                db.add(promotion)

        db_order = Order(
            user_id=cart.user_id,
            cart_id=order.cart_id,
            shipping_address=order.shipping_address,
            billing_address=order.billing_address,
            payment_method=order.payment_method,
            total=total,
            status="pending"
        )
        cart.status = "completed"
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        order_items = [
            {
                "product_id": str(item.product_id),
                "name": item.product.name,
                "price": float(item.product.price),
                "quantity": item.quantity,
                "total": float(item.product.price * item.quantity)
            }
            for item in cart.items
        ]

        return OrderSchema(
            id=db_order.id,
            user_id=db_order.user_id,
            cart_id=db_order.cart_id,
            total=float(db_order.total),
            status=db_order.status,
            shipping_address=db_order.shipping_address,
            billing_address=db_order.billing_address,
            payment_method=db_order.payment_method,
            items=order_items,
            applied_discount=applied_discount if applied_discount > 0 else None
        )

    except (SQLAlchemyError, ValueError) as e:
        db.rollback()
        raise Exception(f"Błąd bazy danych lub walidacji podczas tworzenia zamówienia: {str(e)}")


def get_order(db: Session, order_id: UUID, user_id: UUID):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        return None

    items = db.query(CartItem).filter(CartItem.cart_id == order.cart_id).all()

    order_items = [
        {
            "product_id": item.product_id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "total": (item.product.price * item.quantity)
        }
        for item in items
    ]

    return OrderSchema(
        id=order.id,
        user_id=order.user_id,
        cart_id=order.cart_id,
        total=order.total,
        status=order.status,
        shipping_address=order.shipping_address,
        billing_address=order.billing_address,
        payment_method=order.payment_method,
        items=order_items
    )

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    try:
        orders = db.query(Order).offset(skip).limit(limit).all()
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
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching orders: {str(e)}")

def get_user_orders(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    """
    Pobiera zamówienia dla konkretnego użytkownika.
    """
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
        result = []
        for order in orders:
            items = db.query(CartItem).options(joinedload(CartItem.product)).filter(CartItem.cart_id == order.cart_id).all()
            order_items = [
                {
                    "product_id": str(item.product_id),
                    "name": item.product.name,
                    "price": float(item.product.price),
                    "quantity": item.quantity,
                    "total": float(item.product.price * item.quantity)
                }
                for item in items
            ]
            result.append(
                OrderSchema(
                    id=order.id,
                    user_id=order.user_id,
                    cart_id=order.cart_id,
                    shipping_address=order.shipping_address,
                    billing_address=order.billing_address,
                    payment_method=order.payment_method,
                    status=order.status if order.status else "pending",
                    total=float(order.total),
                    applied_discount=order.applied_discount if order.applied_discount else None,
                    promotion_code=order.promotion_code if order.promotion_code else None,
                    items=order_items
                )
            )
        return result
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching user orders: {str(e)}")

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    try:
        categories = db.query(Category).offset(skip).limit(limit).all()
        return categories
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching categories: {str(e)}")

def create_user(db: Session, user: UserRegister):
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email.lower(),
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {
            "id": str(db_user.id),
            "email": db_user.email
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Database error while creating user: {str(e)}")

def get_user(db: Session, user_id: UUID = None, email: str = None):
    try:
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
        elif email:
            user = db.query(User).filter(User.email == email.lower()).first()
        else:
            return None
        if not user:
            return None
        return {
            "id": str(user.id),
            "email": user.email
        }
    except SQLAlchemyError as e:
        raise Exception(f"Database error while retrieving user: {str(e)}")

def get_user_by_email(db: Session, email: str):
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user:
            return None
        return user
    except SQLAlchemyError as e:
        raise Exception(f"Database error while retrieving user: {str(e)}")

def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> User:
    """
    Aktualizuje dane użytkownika (np. email).
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise ValueError("Użytkownik nie znaleziony")

        if user_update.email and user_update.email != db_user.email:
            if db.query(User).filter(User.email == user_update.email).first():
                raise ValueError("Email jest już zajęty")
            db_user.email = user_update.email

        db.commit()
        db.refresh(db_user)
        return db_user
    except (SQLAlchemyError, ValueError) as e:
        db.rollback()
        raise Exception(f"Błąd podczas aktualizacji użytkownika: {str(e)}")


def change_user_password(db: Session, user_id: UUID, change_password: ChangePassword) -> bool:
    """
    Zmienia hasło użytkownika po zweryfikowaniu obecnego hasła.
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise ValueError("Użytkownik nie znaleziony")

        if not verify_password(change_password.current_password, db_user.hashed_password):
            raise ValueError("Bieżące hasło jest nieprawidłowe")

        db_user.hashed_password = get_password_hash(change_password.new_password)
        db.commit()
        return True
    except (SQLAlchemyError, ValueError) as e:
        db.rollback()
        raise Exception(f"Błąd podczas zmiany hasła: {str(e)}")


def delete_user(db: Session, user_id: UUID) -> bool:
    """
    Usuwa konto użytkownika.
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise ValueError("Użytkownik nie znaleziony")

        db.delete(db_user)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Błąd podczas usuwania użytkownika: {str(e)}")