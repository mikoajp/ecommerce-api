🛒 E-commerce Backend
A backend for an e-commerce application built with FastAPI (Python) and powered by a PostgreSQL database.
It provides functionality for managing products, carts, orders, promotions, categories, and user accounts.

✨ Features
✅ Product management (CRUD operations)

✅ Cart creation and item management

✅ Order creation and retrieval with optional discount (applied_discount)

✅ Promotion management

✅ Category listing

✅ User authentication and profile management with JWT

🛠️ Technologies
Framework: FastAPI

ORM: SQLAlchemy

Database: PostgreSQL

Migrations: Alembic

Deployment: Heroku

⚙️ Prerequisites
Python 3.9+

PostgreSQL

Git

Heroku CLI (for deployment)

🚀 Local Setup and Running
1. Clone the repository:
bash
Kopiuj
Edytuj
git clone https://github.com/<your_username>/<your_repository>.git
cd <your_repository>
2. Create a virtual environment and install dependencies:
bash
Kopiuj
Edytuj
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
3. Set up the database:
Create a PostgreSQL database:

bash
Kopiuj
Edytuj
createdb ecommerce_db
Create a .env file in the root directory with the following variables:

env
Kopiuj
Edytuj
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/ecommerce_db
SECRET_KEY=<your_secret_key>
4. Run database migrations:
bash
Kopiuj
Edytuj
alembic upgrade head
5. Start the server:
bash
Kopiuj
Edytuj
uvicorn main:app --reload --host 0.0.0.0 --port 8000
The backend will be available at:
➡️ http://localhost:8000

☁️ Deployment to Heroku
1. Log in to Heroku:
bash
Kopiuj
Edytuj
heroku login
2. Create a Heroku app:
bash
Kopiuj
Edytuj
heroku create ecommerce-api118
3. Set environment variables:
bash
Kopiuj
Edytuj
heroku config:set DATABASE_URL=<your_postgresql_url>
heroku config:set SECRET_KEY=<your_secret_key>
4. Deploy the application:
bash
Kopiuj
Edytuj
git push heroku main
5. Run migrations on Heroku:
bash
Kopiuj
Edytuj
heroku run "alembic upgrade head"
📂 Project Structure
bash
Kopiuj
Edytuj
ecommerce-backend/
├── migrations/        # Alembic migrations
├── models.py          # SQLAlchemy models
├── schemas.py         # Pydantic schemas
├── crud.py            # CRUD logic
├── main.py            # Main FastAPI file
├── database.py        # Database configuration
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
📖 API Endpoints
🛍️ Products
Method	Endpoint	Description
POST	/products/	Create a new product
GET	/products/	Retrieve a list of products
GET	/products/{id}	Retrieve product by ID
🛒 Carts
Method	Endpoint	Description
POST	/carts/	Create a new cart
POST	/carts/{cart_id}/items/	Add a product to the cart
GET	/carts/{cart_id}	Retrieve cart contents
DELETE	/carts/{cart_id}/items/{product_id}	Remove a product from the cart
PUT	/carts/{cart_id}/items/{product_id}	Update quantity of a product in cart
📦 Orders
Method	Endpoint	Description
POST	/orders/	Create a new order
GET	/orders/	Retrieve all orders
GET	/orders/{order_id}	Retrieve order by ID
🎁 Promotions
Method	Endpoint	Description
POST	/promotions/	Create a new promotion
GET	/promotions/	Retrieve all promotions
🗂️ Categories
Method	Endpoint	Description
GET	/categories/	Retrieve all categories
🔐 Authentication
Method	Endpoint	Description
POST	/auth/register	Register a new user
POST	/auth/login	Login user and obtain JWT token
GET	/auth/protected	Access protected resource (JWT)
👤 User Management
Method	Endpoint	Description
PUT	/users/me	Update user profile
DELETE	/users/me	Delete user account
PUT	/users/me/password	Change user password
GET	/users/me/orders	Retrieve user's orders (with discounts)
📝 API Documentation
➡️ Swagger UI:
https://ecommerce-api118-c945ac1acfd7.herokuapp.com/docs

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.
