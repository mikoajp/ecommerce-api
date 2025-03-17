from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User
from schemas import ProductCreate, Product, CartItemBase, Cart, OrderCreate, Order, CartCreate, Category, UserCreate, User
from crud import (
    create_product, get_products, get_product,
    add_to_cart, get_cart, remove_from_cart,
    create_order, get_orders, create_cart,
    get_categories, update_cart_item_quantity,create_user, get_user
)
from typing import List
from uuid import UUID

app = FastAPI()

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product Endpoints
@app.post("/products/", response_model=Product)
def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, product)

@app.get("/products/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_products(db, skip=skip, limit=limit)

@app.get("/products/{id}", response_model=Product)
def read_product(id: UUID, db: Session = Depends(get_db)):
    product = get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Cart Endpoints
@app.post("/carts/", response_model=Cart)
def create_cart_endpoint(cart: CartCreate, db: Session = Depends(get_db)):
    return create_cart(db, cart)

@app.post("/carts/{cart_id}/items/", response_model=Cart)
def add_to_cart_endpoint(cart_id: UUID, cart_item: CartItemBase, db: Session = Depends(get_db)):
    cart = add_to_cart(db, cart_id, cart_item)
    if not cart:
        raise HTTPException(status_code=400, detail="Could not add item to cart (cart not active or insufficient stock)")
    return cart

@app.get("/carts/{cart_id}", response_model=Cart)
def read_cart(cart_id: UUID, db: Session = Depends(get_db)):
    cart = get_cart(db, cart_id)
    return cart

@app.delete("/carts/{cart_id}/items/{product_id}", response_model=Cart)
def remove_from_cart_endpoint(cart_id: UUID, product_id: UUID, db: Session = Depends(get_db)):
    cart = remove_from_cart(db, cart_id, product_id)
    if not cart:
        raise HTTPException(status_code=400, detail="Could not remove item from cart (cart not active)")
    return cart

@app.put("/carts/{cart_id}/items/{product_id}", response_model=Cart)
def update_cart_item_quantity_endpoint(cart_id: UUID, product_id: UUID, quantity: int, db: Session = Depends(get_db)):
    updated_cart = update_cart_item_quantity(db, cart_id, product_id, quantity)
    if not updated_cart:
        raise HTTPException(status_code=400, detail="Could not update item quantity (cart not active or insufficient stock)")
    return updated_cart

# Order Endpoints
@app.post("/orders/", response_model=Order)
def create_order_endpoint(order: OrderCreate, db: Session = Depends(get_db)):
    created_order = create_order(db, order)
    if not created_order:
        raise HTTPException(status_code=400, detail="Could not create order (cart not active or empty)")
    return created_order

@app.get("/orders/", response_model=List[Order])
def read_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_orders(db, skip=skip, limit=limit)

# Category Endpoint
@app.get("/categories/", response_model=List[Category])
def read_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    categories = get_categories(db, skip=skip, limit=limit)
    return categories


@app.post("/users/", response_model=User, status_code=201)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        db_user = create_user(db, user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=User)
def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/email/{email}", response_model=User)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = get_user(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Database Initialization
@app.get("/init-db")
def init_db(db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    return {"message": "Database initialized"}