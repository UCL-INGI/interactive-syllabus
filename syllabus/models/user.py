import hmac
from hmac import HMAC

from sqlalchemy import Column, String, Boolean
from syllabus.database import Base
from hashlib import sha512, pbkdf2_hmac, sha256


class User(Base):
    __tablename__ = 'users'
    username = Column(String(40), primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False)
    full_name = Column(String(50))
    hash_password = Column(String(80))
    change_password_url = Column(String(50))
    right = Column(String(30))
    activated = Column(Boolean(), nullable=False, default=False)

    def __init__(self, name, email, hash_password, full_name=None, change_password_url=None, right=None,
                 activated=False):
        self.username = name
        self.email = email
        self.hash_password = hash_password
        self.full_name = full_name
        self.change_password_url = change_password_url
        self.right = right
        self.activated = activated

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


def hash_password_func(email, password, global_salt, n_iterations):
    if global_salt is None:
        return sha512(password.encode()).hexdigest()
    return pbkdf2_hmac('sha512',
                       password=password.encode(),
                       salt=HMAC(global_salt.encode(), email.encode(), sha256).digest(),
                       iterations=n_iterations).hex()


def _get_activation_mac(email: str, secret: str, timestamp: int):
    return HMAC(secret.encode(), "{}.{}.activate".format(email, timestamp).encode(), sha256)


def get_activation_mac(email: str, secret: str, timestamp: int):
    return _get_activation_mac(email=email, secret=secret, timestamp=timestamp).hexdigest()


def verify_activation_mac(email: str, secret: str, timestamp: int, mac_to_verify: str):
    return hmac.compare_digest(get_activation_mac(email=email, secret=secret, timestamp=timestamp), mac_to_verify)


class UserAlreadyExists(Exception):
    pass
