from pydantic import BaseModel, field_validator, UUID4
from typing import List, Optional
from uuid import UUID

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
        if v > 1000000:
            raise ValueError("Price must not exceed 1,000,000")
        return v

    @field_validator("old_price", mode="before")
    def old_price_must_be_valid(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v <= 0:
                raise ValueError("Old price must be positive if provided")
            if v > 10000:
                raise ValueError("Old price must not exceed 10,000")
        return v

    @field_validator("stock")
    def stock_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock cannot be negative")
        return v

    @field_validator("sku")
    def sku_must_be_valid(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("SKU cannot be empty")
        if len(v) > 50:
            raise ValueError("SKU must not exceed 50 characters")
        return v.strip()

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: UUID
    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    product_id: UUID
    quantity: int

    @field_validator("quantity")
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantity must be positive")
        if v > 1000:
            raise ValueError("Quantity must not exceed 1000")
        return v

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: UUID
    cart_id: UUID
    name: Optional[str] = None
    price: Optional[float] = None
    total: Optional[float] = None

    @field_validator("price", mode="before")
    def price_must_be_valid_if_provided(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Price must be positive if provided")
        return v

    @field_validator("total", mode="before")
    def total_must_be_valid_if_provided(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Total cannot be negative if provided")
        return v

    class Config:
        from_attributes = True

class CartBase(BaseModel):
    user_id: UUID

class CartCreate(CartBase):
    pass

class Cart(CartBase):
    id: UUID
    items: List[CartItem] = []
    total: float
    status: str

    @field_validator("total")
    def total_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Total cannot be negative")
        return v

    @field_validator("status")
    def status_must_be_valid(cls, v: str) -> str:
        valid_statuses = {"active", "completed", "abandoned"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    cart_id: UUID
    shipping_address: str
    billing_address: Optional[str] = None
    payment_method: str

    @field_validator("shipping_address")
    def shipping_address_must_not_be_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Shipping address cannot be empty")
        if len(v) > 200:
            raise ValueError("Shipping address must not exceed 200 characters")
        return v.strip()

    @field_validator("billing_address", mode="before")
    def billing_address_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError("Billing address cannot be empty if provided")
        if v is not None and len(v) > 200:
            raise ValueError("Billing address must not exceed 200 characters")
        return v.strip() if v else v

    @field_validator("payment_method")
    def payment_method_must_be_valid(cls, v: str) -> str:
        valid_methods = {"credit_card", "paypal", "bank_transfer"}
        if not v or v.strip() == "":
            raise ValueError("Payment method cannot be empty")
        if v not in valid_methods:
            raise ValueError(f"Payment method must be one of {valid_methods}")
        return v

class Order(BaseModel):
    id: UUID
    user_id: UUID
    cart_id: UUID
    items: List[CartItem]
    total: float
    shipping_address: str
    billing_address: Optional[str] = None
    payment_method: str
    status: str

    @field_validator("total")
    def total_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Total cannot be negative")
        return v

    @field_validator("status")
    def status_must_be_valid(cls, v: str) -> str:
        valid_statuses = {"pending", "processing", "shipped", "delivered", "cancelled"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v

    class Config:
        from_attributes = True