from fastapi import FastAPI, Depends, HTTPException, Path, Query, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User
from schemas import ProductCreate, Product, CartItemBase, Cart, OrderCreate, Order, CartCreate, Category, UserCreate, \
    User
from crud import (
    create_product, get_products, get_product,
    add_to_cart, get_cart, remove_from_cart,
    create_order, get_orders, create_cart,
    get_categories, update_cart_item_quantity, create_user, get_user
)
from typing import List, Dict, Any
from uuid import UUID

# Inicjalizacja aplikacji FastAPI z metadanymi
app = FastAPI(
    title="E-Commerce API",
    description="""
# API E-Commerce

API dla sklepu internetowego umożliwiające zarządzanie produktami, koszykami zakupowymi i zamówieniami.

## Funkcjonalności:

* **Produkty** - przeglądanie i zarządzanie produktami
* **Koszyki** - zarządzanie koszykami zakupowymi
* **Zamówienia** - składanie i śledzenie zamówień
* **Kategorie** - przeglądanie kategorii produktów
* **Użytkownicy** - zarządzanie kontami użytkowników

## Statusy koszyków:

* **active** - aktywny, można dodawać/usuwać produkty
* **completed** - przekształcony w zamówienie
* **abandoned** - porzucony przez użytkownika
    """,
    version="1.0.0",
    docs_url=None,  # Wyłączamy domyślną dokumentację
    redoc_url="/redoc"
)

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Niestandardowy endpoint dla Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Dokumentacja API",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,  # Ukryj sekcję "Schemas" domyślnie
            "docExpansion": "list",  # Endpoints zwinięte domyślnie
            "displayRequestDuration": True,  # Pokaż czas wykonania żądania
            "filter": True,  # Włącz wyszukiwarkę
            "tryItOutEnabled": True,  # Włącz tryb testowy domyślnie
            "syntaxHighlight.theme": "monokai"  # Kolorowanie składni
        }
    )


# Niestandardowa generacja schematu OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Dodaj informacje kontaktowe
    openapi_schema["info"]["contact"] = {
        "name": "Zespół wsparcia",
        "url": "https://example.com/contact",
        "email": "support@example.com"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ==========================================
# Product Endpoints
# ==========================================

@app.post(
    "/products/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    tags=["Produkty"],
    summary="Utwórz nowy produkt",
    description="Tworzy nowy produkt w sklepie z podanymi danymi."
)
def create_product_endpoint(
        product: ProductCreate = Body(...,
                                      description="Dane produktu do utworzenia",
                                      example={
                                          "name": "Smartfon Galaxy S21",
                                          "description": "Najnowszy model z serii Galaxy",
                                          "price": 2999.99,
                                          "stock": 50,
                                          "image": "https://example.com/images/galaxy-s21.jpg",
                                          "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                                          "sku": "GAL-S21-BLK-128"
                                      }
                                      ),
        db: Session = Depends(get_db)
):
    """
    Tworzy nowy produkt w bazie danych.
    """
    return create_product(db, product)


@app.get(
    "/products/",
    response_model=List[Product],
    tags=["Produkty"],
    summary="Pobierz listę produktów",
    description="Zwraca paginowaną listę wszystkich dostępnych produktów."
)
def read_products(
        skip: int = Query(0, ge=0, description="Liczba produktów do pominięcia (paginacja)"),
        limit: int = Query(10, ge=1, le=100, description="Maksymalna liczba produktów do pobrania"),
        db: Session = Depends(get_db)
):
    """
    Pobiera listę produktów z opcjonalną paginacją.
    """
    return get_products(db, skip=skip, limit=limit)


@app.get(
    "/products/{id}",
    response_model=Product,
    tags=["Produkty"],
    summary="Pobierz szczegóły produktu",
    description="Zwraca szczegółowe informacje o produkcie o podanym ID.",
    responses={
        404: {"description": "Produkt nie został znaleziony"}
    }
)
def read_product(
        id: UUID = Path(..., description="Unikalne ID produktu do pobrania"),
        db: Session = Depends(get_db)
):
    """
    Pobiera szczegóły pojedynczego produktu.
    """
    product = get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nie został znaleziony")
    return product


# ==========================================
# Cart Endpoints
# ==========================================

@app.post(
    "/carts/",
    response_model=Cart,
    status_code=status.HTTP_201_CREATED,
    tags=["Koszyki"],
    summary="Utwórz nowy koszyk",
    description="Tworzy nowy koszyk dla użytkownika."
)
def create_cart_endpoint(
        cart: CartCreate = Body(...,
                                description="Dane koszyka do utworzenia",
                                example={
                                    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9"
                                }
                                ),
        db: Session = Depends(get_db)
):
    """
    Tworzy nowy, pusty koszyk dla użytkownika.
    """
    return create_cart(db, cart)


@app.post(
    "/carts/{cart_id}/items/",
    response_model=Cart,
    tags=["Koszyki"],
    summary="Dodaj produkt do koszyka",
    description="Dodaje produkt do koszyka w określonej ilości.",
    responses={
        400: {
            "description": "Nie można dodać produktu do koszyka (koszyk nieaktywny lub niewystarczająca ilość w magazynie)"}
    }
)
def add_to_cart_endpoint(
        cart_id: UUID = Path(..., description="ID koszyka"),
        cart_item: CartItemBase = Body(...,
                                       description="Dane produktu do dodania",
                                       example={
                                           "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                           "quantity": 2
                                       }
                                       ),
        db: Session = Depends(get_db)
):
    """
    Dodaje produkt do koszyka.
    """
    cart = add_to_cart(db, cart_id, cart_item)
    if not cart:
        raise HTTPException(status_code=400,
                            detail="Nie można dodać produktu do koszyka (koszyk nieaktywny lub niewystarczająca ilość w magazynie)")
    return cart


@app.get(
    "/carts/{cart_id}",
    response_model=Cart,
    tags=["Koszyki"],
    summary="Pobierz zawartość koszyka",
    description="Zwraca szczegółowe informacje o koszyku i jego zawartości."
)
def read_cart(
        cart_id: UUID = Path(..., description="ID koszyka do pobrania"),
        db: Session = Depends(get_db)
):
    """
    Pobiera zawartość koszyka.
    """
    cart = get_cart(db, cart_id)
    return cart


@app.delete(
    "/carts/{cart_id}/items/{product_id}",
    response_model=Cart,
    tags=["Koszyki"],
    summary="Usuń produkt z koszyka",
    description="Usuwa produkt z koszyka.",
    responses={
        400: {"description": "Nie można usunąć produktu z koszyka (koszyk nieaktywny)"}
    }
)
def remove_from_cart_endpoint(
        cart_id: UUID = Path(..., description="ID koszyka"),
        product_id: UUID = Path(..., description="ID produktu do usunięcia"),
        db: Session = Depends(get_db)
):
    """
    Usuwa produkt z koszyka.
    """
    cart = remove_from_cart(db, cart_id, product_id)
    if not cart:
        raise HTTPException(status_code=400, detail="Nie można usunąć produktu z koszyka (koszyk nieaktywny)")
    return cart


@app.put(
    "/carts/{cart_id}/items/{product_id}",
    response_model=Cart,
    tags=["Koszyki"],
    summary="Zaktualizuj ilość produktu",
    description="Aktualizuje ilość określonego produktu w koszyku.",
    responses={
        400: {
            "description": "Nie można zaktualizować ilości (koszyk nieaktywny lub niewystarczająca ilość w magazynie)"}
    }
)
def update_cart_item_quantity_endpoint(
        cart_id: UUID = Path(..., description="ID koszyka"),
        product_id: UUID = Path(..., description="ID produktu"),
        quantity: int = Query(..., gt=0, description="Nowa ilość produktu"),
        db: Session = Depends(get_db)
):
    """
    Aktualizuje ilość produktu w koszyku.
    """
    updated_cart = update_cart_item_quantity(db, cart_id, product_id, quantity)
    if not updated_cart:
        raise HTTPException(status_code=400,
                            detail="Nie można zaktualizować ilości (koszyk nieaktywny lub niewystarczająca ilość w magazynie)")
    return updated_cart


# ==========================================
# Order Endpoints
# ==========================================

@app.post(
    "/orders/",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    tags=["Zamówienia"],
    summary="Utwórz nowe zamówienie",
    description="""
    Tworzy nowe zamówienie na podstawie koszyka.
    Proces zamówienia:
    1. Sprawdza dostępność produktów
    2. Zmniejsza stany magazynowe
    3. Oznacza koszyk jako ukończony
    4. Tworzy nowe zamówienie
    """,
    responses={
        400: {"description": "Nie można utworzyć zamówienia (koszyk nieaktywny lub pusty)"}
    }
)
def create_order_endpoint(
        order: OrderCreate = Body(...,
                                  description="Dane zamówienia do utworzenia",
                                  example={
                                      "cart_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                      "shipping_address": "ul. Przykładowa 123, 00-000 Warszawa",
                                      "billing_address": "ul. Przykładowa 123, 00-000 Warszawa",
                                      "payment_method": "card"
                                  }
                                  ),
        db: Session = Depends(get_db)
):
    """
    Tworzy nowe zamówienie na podstawie koszyka.
    """
    created_order = create_order(db, order)
    if not created_order:
        raise HTTPException(status_code=400, detail="Nie można utworzyć zamówienia (koszyk nieaktywny lub pusty)")
    return created_order


@app.get(
    "/orders/",
    response_model=List[Order],
    tags=["Zamówienia"],
    summary="Pobierz listę zamówień",
    description="Zwraca paginowaną listę wszystkich zamówień."
)
def read_orders(
        skip: int = Query(0, ge=0, description="Liczba zamówień do pominięcia (paginacja)"),
        limit: int = Query(10, ge=1, le=100, description="Maksymalna liczba zamówień do pobrania"),
        db: Session = Depends(get_db)
):
    """
    Pobiera listę wszystkich zamówień.
    """
    return get_orders(db, skip=skip, limit=limit)


# ==========================================
# Category Endpoint
# ==========================================

@app.get(
    "/categories/",
    response_model=List[Category],
    tags=["Kategorie"],
    summary="Pobierz listę kategorii",
    description="Zwraca listę wszystkich kategorii produktów."
)
def read_categories(
        skip: int = Query(0, ge=0, description="Liczba kategorii do pominięcia"),
        limit: int = Query(10, ge=1, le=100, description="Maksymalna liczba kategorii do pobrania"),
        db: Session = Depends(get_db)
):
    """
    Pobiera listę kategorii produktów.
    """
    categories = get_categories(db, skip=skip, limit=limit)
    return categories


# ==========================================
# User Endpoints
# ==========================================

@app.post(
    "/users/",
    response_model=User,
    status_code=201,
    tags=["Użytkownicy"],
    summary="Utwórz nowego użytkownika",
    description="Tworzy nowe konto użytkownika z podanym adresem email.",
    responses={
        400: {"description": "Email już zarejestrowany"},
        500: {"description": "Błąd serwera podczas tworzenia użytkownika"}
    }
)
def create_user_endpoint(
        user: UserCreate = Body(...,
                                description="Dane użytkownika do utworzenia",
                                example={
                                    "email": "user@example.com"
                                }
                                ),
        db: Session = Depends(get_db)
):
    """
    Tworzy nowego użytkownika.
    """
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email już zarejestrowany")
        db_user = create_user(db, user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/users/{user_id}",
    response_model=User,
    tags=["Użytkownicy"],
    summary="Pobierz użytkownika po ID",
    description="Zwraca dane użytkownika o podanym ID.",
    responses={
        404: {"description": "Użytkownik nie został znaleziony"}
    }
)
def get_user_by_id(
        user_id: UUID = Path(..., description="Unikalne ID użytkownika"),
        db: Session = Depends(get_db)
):
    """
    Pobiera użytkownika po ID.
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie został znaleziony")
    return user


@app.get(
    "/users/email/{email}",
    response_model=User,
    tags=["Użytkownicy"],
    summary="Pobierz użytkownika po adresie email",
    description="Zwraca dane użytkownika o podanym adresie email.",
    responses={
        404: {"description": "Użytkownik nie został znaleziony"}
    }
)
def get_user_by_email(
        email: str = Path(..., description="Adres email użytkownika"),
        db: Session = Depends(get_db)
):
    """
    Pobiera użytkownika po adresie email.
    """
    user = get_user(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie został znaleziony")
    return user


# ==========================================
# Database Initialization
# ==========================================

@app.get(
    "/init-db",
    tags=["System"],
    summary="Inicjalizacja bazy danych",
    description="Tworzy wszystkie wymagane tabele w bazie danych.",
    include_in_schema=False  # Ukryj endpoint w dokumentacji (opcjonalnie)
)
def init_db(db: Session = Depends(get_db)):
    """
    Inicjalizuje bazę danych, tworząc wszystkie tabele.
    """
    Base.metadata.create_all(bind=engine)
    return {"message": "Baza danych została zainicjalizowana"}