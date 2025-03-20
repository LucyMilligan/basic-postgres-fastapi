from typing import Annotated
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select



#create database models - pydantic sqlmodel, with primary keys indicated

class User(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    name: str
    email: str

class Activity(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    # user_id: int = Field(foreign_key="User.user_id")
    activity: str
    distance_km: float
    date_updated: str

#create an engine - sqlalchemy engine (holds connection to db)
#using sqlite here as it is more simple
sqlite_file_name = "basic_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False} #allows fastapi to use the same sqlite database in different threads
engine = create_engine(sqlite_url, connect_args=connect_args)

#create tables for all table models
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

#create session dependancy (stored object in memory, keeps track of changes to data, then uses
#the engine to communicate to the database). Yield - provide a new session for each request
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

#create tables on startup
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#create a user / activity
#can use the same sqlmodel as a pydantic model
@app.post("/users/")
def create_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post("/activities/")
def create_activity(activity: Activity, session: SessionDep) -> Activity:
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


#get users/activities with paginated results
@app.get("/users/")
def get_users(session: SessionDep, offset: int = 0, limit: int = 10) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.get("/activities/")
def get_users(session: SessionDep, offset: int = 0, limit: int = 10) -> list[Activity]:
    activities = session.exec(select(Activity).offset(offset).limit(limit)).all()
    return activities


#get user/activity by id
@app.get("/users/{user_id}")
def get_user_by_user_id(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/activities/{id}")
def get_activity_by_activity_id(id: int, session: SessionDep) -> Activity:
    activity = session.get(Activity, id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


#delete a user/activity
@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

@app.delete("/activities/{id}")
def delete_activity(id: int, session: SessionDep):
    activity = session.get(Activity, id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    session.delete(activity)
    session.commit()
    return {"ok": True}

