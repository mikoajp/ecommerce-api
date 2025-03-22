# 🛒 E-commerce Backend

A powerful **FastAPI** backend for an e-commerce application, using **PostgreSQL** as its core database. Includes full CRUD operations, authentication, cart management, orders, promotions, and more!

## 🚀 Features

- ✅ **Product management** (CRUD operations)
- ✅ **Cart** creation and item management
- ✅ **Orders** with optional discounts (`applied_discount`)
- ✅ **Promotion** management
- ✅ **Category** listing
- ✅ **JWT**-based authentication and user profile management

## 🛠️ Tech Stack

| Technology | Description |
|------------|-------------|
| 🐍 Python | Backend language |
| ⚡ FastAPI | Web framework |
| 🐘 PostgreSQL | Relational Database |
| 🛠️ SQLAlchemy | ORM |
| 🐾 Alembic | Database migrations |
| ☁️ Heroku | Deployment platform |

## ⚙️ Prerequisites

* Python **3.9+**
* PostgreSQL
* Git
* Heroku CLI (for deployment)

## 📦 Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your_username>/<your_repository>.git
cd <your_repository>
```

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up the database

Create a PostgreSQL database:

```bash
createdb ecommerce_db
```

Add environment variables in a .env file:

```dotenv
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/ecommerce_db
SECRET_KEY=<your_secret_key>
```

### 5️⃣ Run migrations

```bash
alembic upgrade head
```

### 6️⃣ Start the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

🖥️ Visit the app at: http://localhost:8000

## ☁️ Deployment to Heroku

### 🔑 Login to Heroku

```bash
heroku login
```

### 🏗️ Create Heroku app

```bash
heroku create ecommerce-api118
```

### ⚙️ Set environment variables

```bash
heroku config:set DATABASE_URL=<your_postgresql_url>
heroku config:set SECRET_KEY=<your_secret_key>
```

### 🚀 Deploy the app

```bash
git push heroku main
```

### 🛠️ Run migrations on Heroku

```bash
heroku run "alembic upgrade head"
```

🌐 Live API docs: https://ecommerce-api118-c945ac1acfd7.herokuapp.com/docs

## 📁 Project Structure

```
ecommerce-backend/
├── migrations/        # Alembic migrations
├── models.py          # SQLAlchemy models
├── schemas.py         # Pydantic schemas
├── crud.py            # CRUD logic
├── main.py            # FastAPI app entry point
├── database.py        # DB configuration & connection
├── requirements.txt   # Project dependencies
└── README.md          # Documentation
```

## 🔗 API Endpoints Overview

### 🛍️ Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/products/` | Retrieves all products from the database |
| `GET` | `/products/{id}` | Gets details of a specific product by its identifier |
| `POST` | `/products/` | Creates a new product in the database |
| `PUT` | `/products/{id}` | Updates an existing product |
| `DELETE` | `/products/{id}` | Removes a product from the database |

### 🛒 Carts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/carts/` | Creates a new shopping cart |
| `GET` | `/carts/{cart_id}` | Retrieves cart contents |
| `POST` | `/carts/{cart_id}/items/` | Adds a product to the cart |
| `PUT` | `/carts/{cart_id}/items/{product_id}` | Updates product quantity in the cart |
| `DELETE` | `/carts/{cart_id}/items/{product_id}` | Removes a product from the cart |

### 📦 Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/orders/` | Creates a new order based on cart contents |
| `GET` | `/orders/` | Retrieves a list of all orders |
| `GET` | `/orders/{order_id}` | Gets details of a specific order |

### 🎁 Promotions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/promotions/` | Creates a new promotion |
| `GET` | `/promotions/` | Retrieves a list of all available promotions |
| `GET` | `/promotions/{promotion_id}` | Gets details of a specific promotion |

### 🗂️ Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/categories/` | Retrieves a list of all product categories |
| `GET` | `/categories/{category_id}/products` | Gets all products in a specific category |

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Registers a new user |
| `POST` | `/auth/login` | Logs in a user and returns a JWT token |
| `GET` | `/auth/protected` | Example protected endpoint requiring authorization |

### 👤 User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/me` | Retrieves profile data for the logged-in user |
| `PUT` | `/users/me` | Updates user profile data |
| `DELETE` | `/users/me` | Deletes the user account |
| `PUT` | `/users/me/password` | Changes user password |
| `GET` | `/users/me/orders` | Retrieves order history for the logged-in user |
