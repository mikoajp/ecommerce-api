from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from schemas import ProductCreate, CartItemBase, CartCreate, OrderCreate, UserRegister
from models import Product, Cart, CartItem, Order, Category, User
from uuid import UUID
from auth import get_password_hash
from schemas import Order as OrderSchema

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

def create_order(db: Session, order: OrderCreate):
    try:
        cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.id == order.cart_id).first()
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
        db_order = Order(
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
    except (SQLAlchemyError, ValueError) as e:
        db.rollback()
        raise Exception(f"Database or validation error while creating order: {str(e)}")


def get_order(db: Session, order_id: UUID, user_id: UUID):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        return None

    items = db.query(CartItem).filter(CartItem.cart_id == order.cart_id).all()
    order_items = [
        {
            "product_id": item.product_id,
            "name": item.product.name,
            "price": item.price,
            "quantity": item.quantity,
            "total": item.price * item.quantity
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
        items=items
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