# 🏟️ Turf Booking App (Fast API)



## Description
This project is a **Turf Booking Application** built with **Fast API**, designed to simplify and streamline the process of reserving sports turfs. It provides a robust back end API for managing users, turfs, bookings, and schedules.

## 🚀 Features
- User registration and authentication.

- Social authentication with Google single sing-in.

- Turf listing with details (location, availability, pricing)

- Nearby turf search using latitude and longitude.

- Real-time turf availability check.

- Booking creation, update, and cancellation.

- Admin panel for managing turfs and bookings.

- RESTful API with fast response times.

- Integrated with the PostgreSQL database.

  

## 🛠️ Tech Stack
- **Back-end Framework**: FastAPI

- **Database**: SQL Alchemy ORM with PostgreSQL.

- **Authentication**: OAuth2/JWT and Google social authentication.

- **Environment Management**: Pydantic & dotenv

- **Testing**: Pytest

- **Geo location**: Haversine distance logic for location-based filtering

  

## 🔧  Environment Setup

To run this project locally, you need to create and activate a Python virtual environment and install the required dependencies. Below are setup instructions for **Linux**, **Windows**, and **mac OS** systems.

1. **Clone the repository.**

2. **Create and Activate Virtual Environment.**

   #####  Linux / mac OS

   ```
   # Create a virtual environment named "venv"
   python3 -m venv venv
   
   # Activate the virtual environment
   source venv/bin/activate
   ```

   #####  Windows (CMD)

   ```
   :: Create virtual environment
   python -m venv venv
   
   :: Activate virtual environment
   venv\Scripts\activate
   ```

   

3. **Install Dependencies**

   Once the environment is activated:

   ```
   pip install -r requirements.txt
   ```

   

4. ##### Set Up Environment Variables

   Create a `.env` file in the project root directory as instructed in `.sample-env` file in this repository. 

   Example:

   ```
   DATABASE_URL= postgresql://user:password@localhost:5432/db_name
   GOOGLE_CLIENT_ID = your_google_client_id
   GOOGLE_CLIENT_SECRET = your_google_cloud_secret_key
   ```

   

## **🛠️ Alembic Configuration**

   To handle database schema migrations, this project uses **Alembic** with async SQLAlchemy support.

   #### 🔄 Running Alembic Migrations

   1. **Initialize Alembic (first time only):**

   ```
   alembic init alembic
   ```

   1. **Edit `alembic.ini` and `env.py` to use your database URL and async engine**.
       For detailed instructions and examples, follow this excellent guide:
       🔗 [Setup FastAPI project with async SQLAlchemy, Alembic, PostgreSQL and Docker](https://berkkaraal.com/blog/2024/09/19/setup-fastapi-project-with-async-sqlalchemy-2-alembic-postgresql-and-docker/#setup-database-migrations-with-alembic)
   2. **Create a migration revision:**

   ```
   alembic revision --autogenerate -m "Initial migration"
   ```

3. **Apply migrations:**

   ```
   alembic upgrade head
   ```

   > ✅ Use Alembic only when your virtual environment is activated and your database is running.



### ▶️ Run the Project

After setting up your environment and installing dependencies, follow these steps to start the FastAPI server:

#### 🔹 Start the Application

```
uvicorn app.main:app --reload
```

#### 🔹 Access API Docs

FastAPI provides built-in interactive documentation:

- Swagger UI: http://127.0.0.1:8000/docs

- ReDoc: http://127.0.0.1:8000/redoc

    

## 📌 TODOs

- Add payment gateway integration

- Add calendar-based booking view



