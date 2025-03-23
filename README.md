# basic-postgres-fastapi

Practice project to try out creating an API with FastAPI and using SQLmodels to connect to a SQLite database.

## Setup

Create a virtual environment and install the requirements

```pip install requirements.txt```

## To run the application

If database does not exist, run:

```psql -f create.sql```

To run the application:

```uvicorn main:app --reload --port <port: int>```

To test the requests, use the browser and localhost:<port: int>/docs
