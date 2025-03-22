# 🛒 E-commerce Backend

A powerful **FastAPI** backend for an e-commerce application, using **PostgreSQL** as its core database.  
Includes full CRUD operations, authentication, cart management, orders, promotions, and more!

---

## 🚀 Features
✅ **Product management** (CRUD operations)  
✅ **Cart** creation and item management  
✅ **Orders** with optional discounts (`applied_discount`)  
✅ **Promotion** management  
✅ **Category** listing  
✅ **JWT**-based authentication and user profile management  

---

## 🛠️ Tech Stack
| Technology  | Description           |
|-------------|-----------------------|
| 🐍 Python   | Backend language      |
| ⚡ FastAPI   | Web framework         |
| 🐘 PostgreSQL | Relational Database |
| 🛠️ SQLAlchemy | ORM                 |
| 🐾 Alembic   | Database migrations   |
| ☁️ Heroku   | Deployment platform   |

---

## ⚙️ Prerequisites

- Python **3.9+**
- PostgreSQL
- Git
- Heroku CLI (for deployment)

---

## 📦 Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your_username>/<your_repository>.git
cd <your_repository>
2️⃣ Create and activate a virtual environment
bash
Kopiuj
Edytuj
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
3️⃣ Install dependencies
bash
Kopiuj
Edytuj
pip install -r requirements.txt
4️⃣ Set up the database
Create a PostgreSQL database:

bash
Kopiuj
Edytuj
createdb ecommerce_db
Add environment variables in a .env file:

dotenv
Kopiuj
Edytuj
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/ecommerce_db
SECRET_KEY=<your_secret_key>
5️⃣ Run migrations
bash
Kopiuj
Edytuj
alembic upgrade head
6️⃣ Start the server
bash
Kopiuj
Edytuj
uvicorn main:app --reload --host 0.0.0.0 --port 8000
🖥️ Visit the app at: http://localhost:8000

☁️ Deployment to Heroku
🔑 Login to Heroku
bash
Kopiuj
Edytuj
heroku login
🏗️ Create Heroku app
bash
Kopiuj
Edytuj
heroku create ecommerce-api118
⚙️ Set environment variables
bash
Kopiuj
Edytuj
heroku config:set DATABASE_URL=<your_postgresql_url>
heroku config:set SECRET_KEY=<your_secret_key>
🚀 Deploy the app
bash
Kopiuj
Edytuj
git push heroku main
🛠️ Run migrations on Heroku
bash
Kopiuj
Edytuj
heroku run "alembic upgrade head"
🌐 Live API docs: https://ecommerce-api118-c945ac1acfd7.herokuapp.com/docs

📁 Project Structure
graphql
Kopiuj
Edytuj
ecommerce-backend/
├── migrations/        # Alembic migrations
├── models.py          # SQLAlchemy models
├── schemas.py         # Pydantic schemas
├── crud.py            # CRUD logic
├── main.py            # FastAPI app entry point
├── database.py        # DB configuration & connection
├── requirements.txt   # Project dependencies
└── README.md          # Documentation
🔗 API Endpoints Overview
🛍️ Products
Method	Endpoint	Description
POST	/products/	Create product
GET	/products/	Get all products
GET	/products/{id}	Get product by ID
🛒 Carts
Method	Endpoint	Description
POST	/carts/	Create cart
POST	/carts/{cart_id}/items/	Add item to cart
GET	/carts/{cart_id}	Retrieve cart contents
PUT	/carts/{cart_id}/items/{product_id}	Update item quantity in cart
DELETE	/carts/{cart_id}/items/{product_id}	Remove item from cart
📦 Orders
Method	Endpoint	Description
POST	/orders/	Create order
GET	/orders/	List all orders
GET	/orders/{order_id}	Get order details
🎁 Promotions
Method	Endpoint	Description
POST	/promotions/	Create promotion
GET	/promotions/	List all promotions
🗂️ Categories
Method	Endpoint	Description
GET	/categories/	List all categories
🔐 Authentication
Method	Endpoint	Description
POST	/auth/register	Register user
POST	/auth/login	Login user and return JWT token
GET	/auth/protected	Access protected resource
👤 User Management
Method	Endpoint	Description
PUT	/users/me	Update profile
DELETE	/users/me	Delete account
PUT	/users/me/password	Change password
GET	/users/me/orders	Get your orders (discount included)
