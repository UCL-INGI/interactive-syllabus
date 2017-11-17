from sqlalchemy import Column, String
from syllabus.database import Base
from hashlib import sha512


class User(Base):
    __tablename__ = 'users'
    name = Column(String(40), primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(25))
    last_name = Column(String(25))
    hash_password = Column(String(80))
    change_password_url = Column(String(50))

    def __init__(self, name, email, hash_password, first_name=None, last_name=None, change_password_url=None):
        self.name = name
        self.email = email
        self.hash_password = hash_password
        self.first_name = first_name
        self.last_name = last_name
        self.change_password_url = change_password_url

    def __repr__(self):
        return '<User %r>' % (self.name)


def hash_password(password):
    return sha512(password).hexdigest()
