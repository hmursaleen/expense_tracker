````markdown
# 💸 Expense Tracker API

A secure and scalable **RESTful API** for tracking personal expenses. Built using **Django**, **Django REST Framework**, **JWT Authentication**, and **PostgreSQL via Docker**.

This project allows users to register, log in, and manage their expenses with full CRUD functionality. Expenses can be filtered by date ranges and categorized into predefined types like groceries, clothing, utilities, etc.

---

## 🛠️ Features

- ✅ User Registration and Login
- ✅ JWT Authentication (Access and Refresh tokens)
- ✅ Protected Endpoints for Authenticated Users
- ✅ CRUD for Expense Records
- ✅ Expense Filtering (past week, month, 3 months, or custom range)
- ✅ Predefined Expense Categories
- ✅ PostgreSQL database using Docker
- ✅ Auto-generated API Docs with Swagger & ReDoc
- ✅ Unit and Integration Testing
- ✅ Robust Error Handling and Logging
- ✅ API Versioning (v1)

---

## 🧰 Tech Stack

- **Python 3.10+**
- **Django 4.x**
- **Django REST Framework**
- **Simple JWT**
- **PostgreSQL (Dockerized)**
- **drf-yasg (Swagger)**
- **pytest / Django TestCase**

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/hmursaleen/expense-tracker-api.git
cd expense-tracker-api
````

### 2. Setup Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

POSTGRES_DB=expense_tracker_db
POSTGRES_USER=expense_tracker_user
POSTGRES_PASSWORD=expense_tracker_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 3. Start PostgreSQL via Docker

Make sure Docker is installed and running.

```bash
docker-compose up -d
```

This will start a PostgreSQL container on port `5432`.

### 4. Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply Migrations

```bash
python manage.py migrate
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Now the API is available at: `http://127.0.0.1:8000`

---

## 📂 API Endpoints

### Auth

| Endpoint                      | Method | Description                    |
| ----------------------------- | ------ | ------------------------------ |
| `/api/v1/auth/register/`      | `POST` | Register a new user            |
| `/api/v1/auth/login/`         | `POST` | Login with username & password |
| `/api/v1/auth/token/`         | `POST` | Obtain JWT (access + refresh)  |
| `/api/v1/auth/token/refresh/` | `POST` | Refresh access token           |

### Expenses

| Endpoint                 | Method      | Description                |
| ------------------------ | ----------- | -------------------------- |
| `/api/v1/expenses/`      | `GET`       | List all expenses for user |
| `/api/v1/expenses/`      | `POST`      | Create new expense         |
| `/api/v1/expenses/<id>/` | `GET`       | Retrieve a single expense  |
| `/api/v1/expenses/<id>/` | `PUT/PATCH` | Update an expense          |
| `/api/v1/expenses/<id>/` | `DELETE`    | Delete an expense          |

#### Filter Query Params

| Query Param                                               | Description  |
| --------------------------------------------------------- | ------------ |
| `filter=past_week`                                        | Last 7 days  |
| `filter=past_month`                                       | Last 30 days |
| `filter=last_3_months`                                    | Last 90 days |
| `filter=custom&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | Custom range |

---

## 📒 Expense Categories

The following categories are available as choices:

* `Groceries`
* `Leisure`
* `Electronics`
* `Utilities`
* `Clothing`
* `Health`
* `Others`

---

## 📑 API Documentation

Interactive API documentation is available:

* Swagger: [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/)
* ReDoc: [http://localhost:8000/api/v1/redoc/](http://localhost:8000/api/v1/redoc/)

---

## ✅ Running Tests

To run tests:

```bash
python manage.py test
```

Or with `pytest` if configured:

```bash
pytest
```

---

## 🔐 Security

* Passwords are securely stored using Django’s built-in hashing.
* JWTs are used for secure authentication.
* Permissions ensure users can only manage their own expenses.
* Errors are handled with clear messages and logged internally.

---

## 📁 Project Structure

```
expense_tracker/
├── accounts/          # User registration, login, JWT handling
├── expenses/          # Expense model, views, serializers, filters
├── expense_tracker/   # Settings and main configuration
├── templates/         # (If needed)
├── logs/              # Logged errors (optional)
├── manage.py
├── requirements.txt
└── .env
```

---

## 📌 Future Improvements

* Monthly summaries & charts
* Expense tags and notes
* Export to CSV/PDF
* Email notifications for expense limits
* Dockerizing the entire app (not just DB)

---

## 🧑‍💻 Author

**Habibul Mursaleen**
📧 Email: [habibulmursaleen@gmail.com@example.com](mailto:habibulmursaleen@gmail.com@example.com)
🔗 GitHub: [github.com/hmursaleen](https://github.com/hmursaleen)

---

## ⚖️ License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

````