from sqlalchemy import Column, String, Boolean
from syllabus.database import Base
from hashlib import sha512


class User(Base):
    __tablename__ = 'users'
    username = Column(String(40), primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False)
    full_name = Column(String(50))
    hash_password = Column(String(80))
    change_password_url = Column(String(50))
    right = Column(String(30))
    activated = Column(Boolean(), nullable=False, default=False)
    activation_secret = Column(String(80), unique=True, index=True)

    def __init__(self, name, email, hash_password, full_name=None, change_password_url=None, right=None,
                 activated=False, activation_secret=None):
        self.username = name
        self.email = email
        self.hash_password = hash_password
        self.full_name = full_name
        self.change_password_url = change_password_url
        self.right = right
        self.activated = activated
        self.activation_secret = activation_secret

    def to_dict(self):
        return {"username": self.username, "email": self.email, "right": self.right}

    def __repr__(self):
        return '<User %r>' % (self.username)

    @property
    def admin(self):
        return self.right == "admin"

    @property
    def teacher(self):
        return self.right == "teacher"

    @property
    def at_least_teacher(self):
        return self.right in ["teacher", "admin"]


def hash_password(password):
    return sha512(password).hexdigest()


class UserAlreadyExists(Exception):
    pass
