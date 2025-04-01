# basic-postgres-fastapi

Practice project to try out creating an API with FastAPI and using SQLmodels to connect to a Postgres database. This is in preparation for the fitness_tracker project.

## Setup

Create a virtual environment and install the requirements

```pip install -r requirements.txt```

## To run the application

### If database does not exist:

Create a .env file in the root of the directory, with the following content, updating the username and password with your postgress username and password:

```DB_URL="postgresql://<username>:<password>@localhost:5432/fitness_tracker_test"```

Create the database by running the following in the terminal:

```psql -f create.sql```

### To run the application:

```uvicorn main:app --reload --port <port: int>```

To test the requests, use the browser and localhost:<port: int>/docs
