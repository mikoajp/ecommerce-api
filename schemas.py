from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    stock: int
    image: Optional[str] = None
    category_id: int
    sku: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItem(CartItemBase):
    id: int
    name: str
    price: float
    total: float
    class Config:
        orm_mode = True

class Cart(BaseModel):
    items: List[CartItem]
    total: float

class OrderCreate(BaseModel):
    shipping_address: str
    billing_address: Optional[str] = None
    payment_method: str

class Order(BaseModel):
    id: int
    items: List[CartItem]
    total: float
    shipping_address: str
    billing_address: Optional[str] = None
    payment_method: str
    status: str
    class Config:
        orm_mode = True