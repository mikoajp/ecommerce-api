from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import ProductCreate, Product, CartItemBase, Cart, OrderCreate, Order
from crud import create_product, get_products, get_product, add_to_cart, get_cart, remove_from_cart, create_order

app = FastAPI()

@app.post("/products/", response_model=Product)
def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, product)

@app.get("/products/", response_model=list[Product])
def read_products(db: Session = Depends(get_db)):
    return get_products(db)

@app.get("/products/{id}", response_model=Product)
def read_product(id: int, db: Session = Depends(get_db)):
    return get_product(db, id)

@app.post("/cart/", response_model=Cart)
def add_to_cart_endpoint(cart_item: CartItemBase, db: Session = Depends(get_db)):
    add_to_cart(db, cart_item, user_id=1)
    return get_cart(db, user_id=1)

@app.get("/cart/", response_model=Cart)
def read_cart(db: Session = Depends(get_db)):
    return get_cart(db, user_id=1)

@app.delete("/cart/{product_id}", response_model=Cart)
def remove_from_cart_endpoint(product_id: int, db: Session = Depends(get_db)):
    return remove_from_cart(db, product_id, user_id=1)

@app.post("/orders/", response_model=Order)
def create_order_endpoint(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, order, user_id=1)

@app.get("/orders/", response_model=list[Order])
def read_orders(db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == 1).all()

# Tymczasowy endpoint do inicjalizacji bazy
@app.get("/init-db")
def init_db(db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    return {"message": "Database initialized"}