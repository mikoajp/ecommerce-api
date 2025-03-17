from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import ProductCreate, Product, CartItemBase, Cart, OrderCreate, Order, CartCreate
from crud import (
    create_product, get_products, get_product,
    add_to_cart, get_cart, remove_from_cart,
    create_order, get_orders, create_cart
)
from typing import List
from uuid import UUID

app = FastAPI()


app.add_middleware(
    CORSMiddleware,  # type: ignore
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
        raise HTTPException(status_code=400, detail="Could not add item to cart")
    return get_cart(db, cart_id)

@app.get("/carts/{cart_id}", response_model=Cart)
def read_cart(cart_id: UUID, db: Session = Depends(get_db)):
    cart = get_cart(db, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@app.delete("/carts/{cart_id}/items/{product_id}", response_model=Cart)
def remove_from_cart_endpoint(cart_id: UUID, product_id: UUID, db: Session = Depends(get_db)):
    cart = remove_from_cart(db, cart_id, product_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return get_cart(db, cart_id)

# Order Endpoints
@app.post("/orders/", response_model=Order)
def create_order_endpoint(order: OrderCreate, db: Session = Depends(get_db)):
    created_order = create_order(db, order)
    if not created_order:
        raise HTTPException(status_code=400, detail="Could not create order")
    return created_order

@app.get("/orders/", response_model=List[Order])
def read_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_orders(db, skip=skip, limit=limit)

# Database Initialization
@app.get("/init-db")
def init_db(db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    return {"message": "Database initialized"}