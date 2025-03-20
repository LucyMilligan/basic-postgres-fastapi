from sqlmodel import Session
from models import User, UserCreate
from main import engine


#seed tables
def create_users():
    user_1 = User(name="lucy", email="lucy@gmail.com")
    user_2 = User(name="bob", email="bob@gmail.com")
    user_3 = User(name="sam", email="sam@gmail.com")

    session = Session(engine)

    session.add(user_1)
    session.add(user_2)
    session.add(user_3)