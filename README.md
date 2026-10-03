# 💰 BudgeXP - Personal Budget and Expense Tracker API

A production-ready, RESTful API built with **Django 6.1.1** and **Django REST Framework (DRF)** for managing personal expenses, tracking monthly budget limits, and monitoring spending behavior.

The API is fully deployed on **Render**, backed by a managed **Aiven MySQL** cloud database, featuring automated OpenAPI documentation via Swagger UI, JWT authentication, rate limiting (throttling), and dynamic query filtering.

🚀 **Live Interactive API Documentation:**
https://budgexp-api.onrender.com/api/docs/

🔗 **GitHub Repository:**
https://github.com/thebatssy/BudgeXP

---

## ✨ Features

### 🔐 JWT Authentication

* User registration
* JWT-based authentication using **SimpleJWT**
* Access and refresh token support
* Protected API endpoints

### 📊 Expense Management

* Full CRUD operations for personal expenses
* Track:

  * Category
  * Amount
  * Date
  * Custom notes
* Users can access and manage only their own expenses

### 🎯 Budget Tracking & Analytics

* Define monthly budget limits
* Calculate total monthly spending
* Calculate remaining budget balance
* Detect over-budget conditions
* Dedicated budget summary endpoint

### 🛡️ Rate Limiting & Throttling

* Multi-tier API throttling
* Protection for authentication endpoints against excessive requests
* Rate limiting for resource-intensive analytics endpoints

### 🔎 Filtering & Search

Advanced query filtering powered by **django-filter**.

Supports filtering expenses by:

* Date ranges
* Categories
* Keywords

### 📚 Interactive API Documentation

Self-documenting OpenAPI 3.0 API schema generated using **drf-spectacular**.

Available documentation:

* Swagger UI
* ReDoc

### ⚡ Performance Optimization

* Uses Django ORM efficiently
* `select_related()` used where appropriate to reduce unnecessary database queries and avoid N+1 query patterns

---

## 🛠️ Tech Stack & Architecture

| Component            | Technology                    |
| -------------------- | ----------------------------- |
| Language             | Python                        |
| Backend Framework    | Django 6.1.1                  |
| API Framework        | Django REST Framework 3.18    |
| Database             | MySQL                         |
| Cloud Database       | Aiven Cloud                   |
| Database Driver      | mysqlclient                   |
| Authentication       | djangorestframework-simplejwt |
| API Documentation    | drf-spectacular               |
| API Documentation UI | Swagger UI & ReDoc            |
| Static Files         | WhiteNoise                    |
| WSGI Server          | Gunicorn                      |
| Hosting              | Render                        |

---

## 🔌 API Endpoints

| Method               | Endpoint                        | Description                                     | Authentication |
| -------------------- | ------------------------------- | ----------------------------------------------- | -------------- |
| `POST`               | `/api/register/`                | Register a new user account                     | ❌ No           |
| `POST`               | `/api/token/`                   | Obtain JWT access & refresh tokens              | ❌ No           |
| `POST`               | `/api/token/refresh/`           | Refresh an expired JWT access token             | ❌ No           |
| `GET / POST`         | `/api/expenses/`                | List or create user expenses                    | ✅ Yes          |
| `GET / PUT / DELETE` | `/api/expenses/{id}/`           | Retrieve, update, or delete an expense          | ✅ Yes          |
| `GET / POST`         | `/api/budgets/`                 | View or define monthly budget limits            | ✅ Yes          |
| `GET`                | `/api/expenses/budget-summary/` | Get monthly spending analysis and budget alerts | ✅ Yes          |
| `GET`                | `/api/docs/`                    | Interactive Swagger UI documentation            | ❌ No           |

---

## 📖 API Documentation

The complete API can be explored interactively through Swagger UI:

👉 **https://budgexp-api.onrender.com/api/docs/**

The documentation allows you to:

* Explore available endpoints
* View request and response schemas
* Test API endpoints directly
* Authenticate using JWT
* Understand available parameters and responses

---

# 💻 Local Development Setup

Follow these steps to run BudgeXP locally.

## 1. Prerequisites

Make sure you have the following installed:

* Python 3.x
* MySQL Server
* Git

---

## 2. Clone the Repository

```bash
git clone https://github.com/thebatssy/BudgeXP.git
cd BudgeXP
```

---

## 3. Create and Activate Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file in the root project directory.

```env
SECRET_KEY=your_local_secret_key_here

DEBUG=True

ALLOWED_HOSTS=127.0.0.1,localhost

# Local MySQL Database Credentials
DB_NAME=budgexp_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

> **Note:** Never commit your `.env` file or real database credentials to GitHub.

---

## 6. Create the Database

Create a MySQL database for the project:

```sql
CREATE DATABASE budgexp_db;
```

Make sure your MySQL server is running before proceeding.

---

## 7. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 8. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

Opening the root URL will redirect you to the local Swagger UI documentation.

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

---

# 🌐 Production Deployment

BudgeXP is deployed using:

* **Render** — Web Service / Application Hosting
* **Aiven** — Managed MySQL Cloud Database

The production deployment uses an automated `build.sh` script.

### Deployment Pipeline

The build process:

1. Installs Python dependencies
2. Collects static files using WhiteNoise
3. Applies Django database migrations
4. Starts the application using Gunicorn

---

## 📜 Deployment Script

`build.sh`

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate
```

---

# 🗂️ Project Structure

```text
BudgeXP/
│
├── expenses/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── ...
│
├── budgexp/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── .env
├── .gitignore
├── build.sh
├── manage.py
├── requirements.txt
└── README.md
```

---

# 🔑 Authentication Flow

BudgeXP uses **JWT authentication** through `djangorestframework-simplejwt`.

### 1. Register

```http
POST /api/register/
```

Create a new user account.

### 2. Obtain Tokens

```http
POST /api/token/
```

Returns:

* Access token
* Refresh token

### 3. Access Protected Endpoints

Include the access token in the request header:

```http
Authorization: Bearer <access_token>
```

### 4. Refresh Access Token

```http
POST /api/token/refresh/
```

Use the refresh token to obtain a new access token when the current access token expires.

---

# 📊 Budget Summary

BudgeXP provides a dedicated endpoint for monitoring monthly spending:

```http
GET /api/expenses/budget-summary/
```

The endpoint provides information such as:

* Monthly budget
* Total amount spent
* Remaining budget
* Budget status
* Over-budget alerts

This allows users to monitor their spending against their defined monthly budget.

---

# 🔍 Expense Filtering

Expenses can be filtered using query parameters provided by **django-filter**.

Filtering supports criteria such as:

* Category
* Date range
* Keywords

Example:

```text
/api/expenses/?category=FOOD
```

---

# 🚀 Deployment

The production API is publicly available at:

**Swagger UI:**
https://budgexp-api.onrender.com/api/docs/

**GitHub:**
https://github.com/thebatssy/BudgeXP

---

# 📄 License

This project is intended for educational, portfolio, and development purposes.
