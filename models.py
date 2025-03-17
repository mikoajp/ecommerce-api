from sqlalchemy import Column, String, Float, ForeignKey, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from uuid import uuid4

class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    old_price = Column(Float)
    stock = Column(Integer, nullable=False)
    image = Column(String)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    sku = Column(String, nullable=False, unique=True)
    category = relationship("Category", back_populates="products")
    __table_args__ = (
        CheckConstraint('price >= 0', name='price_non_negative'),
        CheckConstraint('stock >= 0', name='stock_non_negative'),
    )

class Cart(Base):
    __tablename__ = "carts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, default="active")
    items = relationship("CartItem", back_populates="cart")
    __table_args__ = (CheckConstraint("status IN ('active', 'completed', 'abandoned')"),)

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", lazy='joined')
    __table_args__ = (CheckConstraint('quantity > 0', name='quantity_positive'),)

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False)
    shipping_address = Column(String, nullable=False)
    billing_address = Column(String)
    payment_method = Column(String, nullable=False)
    status = Column(String, default="pending")
    total = Column(Float, nullable=False, default=0.0)
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')"),
        CheckConstraint('total >= 0', name='total_non_negative'),
    )

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    email = Column(String, unique=True, nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="category")