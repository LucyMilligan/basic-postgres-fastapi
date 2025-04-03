from datetime import datetime
from sqlmodel import Field, SQLModel
from pydantic import StringConstraints, field_validator
from typing_extensions import Annotated

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

    @field_validator('date', mode='before')
    @classmethod
    def date_valid(cls, value: str):
        try:
            datetime.strptime(value, "%Y/%m/%d")
        except (ValueError, TypeError):
            raise ValueError("Date does not match format 'YYYY/MM/DD'")

    @field_validator('time', mode='before')
    @classmethod
    def time_valid(cls, value: str):
        try:
            datetime.strptime(value, "%H:%M")
        except (ValueError, TypeError):
            raise ValueError("Time does not match format 'HH:MM'")

    @field_validator('moving_time', mode='before')
    @classmethod
    def moving_time_valid(cls, value: str):
        try:
            hours,  minutes, seconds = map(int, value.split(":"))
        except (ValueError, AttributeError):
            raise ValueError("Time does not match format 'HH:MM:SS'")

    @field_validator('activity', mode='before')
    @classmethod
    def activity_valid(cls, value: str):
        valid_activities = ["run", "ride"]
        if value not in valid_activities:
            raise ValueError(f"Activity not in {valid_activities}")
        
    @field_validator('perceived_effort', mode='before')
    @classmethod
    def perceived_effort_valid(cls, value: int):
        try:
            if value < 1 or value > 10:
                raise ValueError("Perceived_effort not in range 1 - 10")
        except TypeError:
            raise ValueError("Perceived_effort not a valid number in the range 1 - 10")


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

    @field_validator('date', mode='before')
    @classmethod
    def date_valid(cls, value: str):
        try:
            datetime.strptime(value, "%Y/%m/%d")
        except (ValueError, TypeError):
            raise ValueError("Date does not match format 'YYYY/MM/DD'")

    @field_validator('time', mode='before')
    @classmethod
    def time_valid(cls, value: str):
        try:
            datetime.strptime(value, "%H:%M")
        except (ValueError, TypeError):
            raise ValueError("Time does not match format 'HH:MM'")

    @field_validator('moving_time', mode='before')
    @classmethod
    def moving_time_valid(cls, value: str):
        try:
            hours,  minutes, seconds = map(int, value.split(":"))
        except (ValueError, AttributeError):
            raise ValueError("Time does not match format 'HH:MM:SS'")

    @field_validator('activity', mode='before')
    @classmethod
    def activity_valid(cls, value: str):
        valid_activities = ["run", "ride"]
        if value not in valid_activities:
            raise ValueError(f"Activity not in {valid_activities}")
        
    @field_validator('perceived_effort', mode='before')
    @classmethod
    def perceived_effort_valid(cls, value: int):
        try:
            if value < 1 or value > 10:
                raise ValueError("Perceived_effort not in range 1 - 10")
        except TypeError:
            raise ValueError("Perceived_effort not a valid number in the range 1 - 10")
        

####### Alternative way of validating fields using regex #######

# class Activity(SQLModel, table=True):
#     __tablename__ = "activity_table"
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="user_table.user_id")
#     date: Annotated[
#         str,
#         StringConstraints(pattern=r"^\d{4}/\d{2}/\d{2}$")]
#     time: Annotated[
#         str,
#         StringConstraints(pattern=r"^\d{2}:\d{2}$")]
#     activity: Annotated[
#         str,
#         StringConstraints(pattern=(r"^(run|ride)$"))]
#     activity_type: str
#     moving_time: Annotated[
#         str,
#         StringConstraints(pattern=r"^\d{2}:\d{2}:\d{2}$")]
#     distance_km: float
#     perceived_effort: Annotated[int, Field(ge=1, le=10)]
#     elevation_m: int | None = None #optional


# class ActivityUpdate(SQLModel): #optional updates to a specific activity id
#     user_id: int | None = None
#     date: Annotated[
#         str,
#         StringConstraints(pattern=r"^\d{4}/\d{2}/\d{2}$")] | None = None
#     time: Annotated[
#         str,
#         StringConstraints(pattern=r"^\d{2}:\d{2}$")] | None = None
#     activity: Annotated[
#         str,
#         StringConstraints(pattern=(r"^(run|ride)$"))] | None = None
#     activity_type: str | None = None
#     moving_time: Annotated[
#         str,
#         StringConstraints(pattern=r"^\d{2}:\d{2}:\d{2}$")] | None = None
#     distance_km: float | None = None
#     perceived_effort: Annotated[int, Field(ge=1, le=10)] | None = None
#     elevation_m: int | None = None