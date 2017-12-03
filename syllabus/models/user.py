from sqlalchemy import Column, String
from syllabus.database import Base
from hashlib import sha512


class User(Base):
    __tablename__ = 'users'
    username = Column(String(40), primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    full_name = Column(String(50))
    hash_password = Column(String(80))
    change_password_url = Column(String(50))

    def __init__(self, name, email, hash_password, full_name=None, change_password_url=None):
        self.username = name
        self.email = email
        self.hash_password = hash_password
        self.full_name = full_name
        self.change_password_url = change_password_url

    def __repr__(self):
        return '<User %r>' % (self.username)


def hash_password(password):
    return sha512(password).hexdigest()
