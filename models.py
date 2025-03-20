from datetime import datetime
from sqlmodel import Field, SQLModel


#create database models - pydantic sqlmodel, with primary keys indicated
#can also inherit from a SQLmodel
class UserBase(SQLModel):
    name: str

class User(UserBase, table=True):
    __tablename__ = "user_table"
    user_id: int | None = Field(default=None, primary_key=True)
    #name comes from UserBase
    email: str

class UserPublic(UserBase):
    user_id: int
    #name comes from UserBase
    #email stays hidden for public users

class UserCreate(UserBase): #for users to create a user (id auto generated)
    #user_id auto generated
    #name comes from UserBase
    email: str

class UserUpdate(UserBase): #optional updates to a specific user_id
    name: str | None = None
    email: str | None = None

class Activity(SQLModel, table=True):
    __tablename__ = "activity_table"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user_table.user_id")
    date: str
    time: str
    activity: str
    activity_type: str
    moving_time: str
    distance_km: float
    perceived_effort: int
    elevation_m: int | None = None #optional

class ActivityCreate(SQLModel):
    #auto generated id
    user_id: int
    date: str
    time: str
    activity: str
    activity_type: str
    moving_time: str
    distance_km: float
    perceived_effort: int
    elevation_m: int | None = None #optional

class ActivityUpdate(SQLModel): #optional updates to a specific activity id
    user_id: int | None = None
    date: str | None = None
    time: str | None = None
    activity: str | None = None
    activity_type: str | None = None
    moving_time: str | None = None
    distance_km: float | None = None
    perceived_effort: int | None = None
    elevation_m: int | None = None
