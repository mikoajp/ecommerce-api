from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Optional
from uuid import UUID
from enum import Enum


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    stock: int
    image: Optional[str] = None
    category_id: UUID
    sku: str

    @field_validator("name")
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Name cannot be empty")
        if len(v) > 100:
            raise ValueError("Name must not exceed 100 characters")
        return v.strip()

    @field_validator("price")
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

    @field_validator("stock")
    def stock_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock must be non-negative")
        return v


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: UUID

    class Config:
        from_attributes = True


# CartItem Schemas
class CartItemBase(BaseModel):
    product_id: UUID
    quantity: int

    @field_validator("quantity")
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v


class CartItem(CartItemBase):
    id: Optional[UUID] = None
    cart_id: Optional[UUID] = None
    product_name: str = Field(..., alias="product.name")
    product_price: float = Field(..., alias="product.price")

    class Config:
        from_attributes = True
        populate_by_name = True


# Cart Schemas
class CartStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class CartBase(BaseModel):
    user_id: UUID


class CartCreate(CartBase):
    pass


class Cart(CartBase):
    id: UUID
    items: List[dict] = []
    total: float
    status: CartStatus

    class Config:
        from_attributes = True


# Order Schemas
class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderCreate(BaseModel):
    cart_id: UUID
    shipping_address: str
    billing_address: Optional[str] = None
    payment_method: str


class Order(OrderCreate):
    id: UUID
    user_id: UUID
    items: List[dict] = []
    total: float
    status: OrderStatus

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str

    @field_validator("name")
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Name cannot be empty")
        if len(v) > 100:
            raise ValueError("Name must not exceed 100 characters")
        return v.strip()


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True


# User Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class User(BaseModel):
    id: UUID
    email: EmailStr

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProtectedResponse(BaseModel):
    message: str
    user: dict