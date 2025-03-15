from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    old_price = Column(Float)
    stock = Column(Integer, nullable=False)
    image = Column(String)
    category_id = Column(Integer, nullable=False)
    sku = Column(String, nullable=False, unique=True)

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    user_id = Column(Integer)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    shipping_address = Column(String, nullable=False)
    billing_address = Column(String)
    payment_method = Column(String, nullable=False)
    status = Column(String, default="pending")