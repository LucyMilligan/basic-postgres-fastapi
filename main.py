from typing import Annotated
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
import os
from dotenv import load_dotenv

from models import Activity, ActivityCreate, ActivityUpdate, User, UserCreate, UserPublic, UserUpdate

load_dotenv()

#create an engine - sqlalchemy engine (holds connection to db)
#sqlite:
# sqlite_file_name = "basic_database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

#postgres:
postgres_url = os.getenv("DB_URL")

# connect_args = {"check_same_thread": False} #allows fastapi to use the same sqlite database in different threads
engine = create_engine(postgres_url)

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
@app.post("/users/", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/activities/", response_model=Activity)
def create_activity(activity: ActivityCreate, session: SessionDep):
    db_activity = Activity.model_validate(activity)
    session.add(db_activity)
    session.commit()
    session.refresh(db_activity)
    return db_activity


#get users/activities with paginated results
@app.get("/users/", response_model=list[UserPublic])
def get_users(session: SessionDep, offset: int = 0, limit: int = 10):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.get("/activities/")
def get_activities(session: SessionDep, offset: int = 0, limit: int = 10) -> list[Activity]:
    activities = session.exec(select(Activity).offset(offset).limit(limit)).all()
    return activities


#get user/activity by id
@app.get("/users/{user_id}", response_model=UserPublic)
def get_user_by_user_id(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/activities/{id}", response_model=Activity)
def get_activity_by_activity_id(id: int, session: SessionDep):
    activity = session.get(Activity, id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


#update a user/activity
@app.patch("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserUpdate, session: SessionDep):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True) #only includes values sent by the client
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@app.patch("/activities/{id}", response_model=Activity)
def update_activity(id: int, activity: ActivityUpdate, session: SessionDep):
    activity_db = session.get(Activity, id)
    if not activity_db:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity_data = activity.model_dump(exclude_unset=True)
    activity_db.sqlmodel_update(activity_data)
    session.add(activity_db)
    session.commit()
    session.refresh(activity_db)
    return activity_db

#delete a user/activity
@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": f"User_id {user_id} deleted"}

@app.delete("/activities/{id}")
def delete_activity(id: int, session: SessionDep):
    activity = session.get(Activity, id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    session.delete(activity)
    session.commit()
    return {"message": f"Activity id {id} deleted"}

