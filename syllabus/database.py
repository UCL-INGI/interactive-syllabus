import os

import binascii
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from syllabus import get_root_path

database_path = os.path.join(get_root_path(), 'database.sqlite')
engine = create_engine('sqlite:///%s' % database_path, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def create_db():
    from syllabus.models.user import User
    change_pwd_bytes: bytes = os.urandom(20)
    change_pwd_hex = binascii.hexlify(change_pwd_bytes).decode()
    u = User('admin', 'admin@localhost', hash_password=None, change_password_url=change_pwd_hex)
    db_session.add(u)
    db_session.commit()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import syllabus.models.user

    Base.metadata.create_all(bind=engine)
    from syllabus.models.user import User
    users = User.query.all()
    if len(users) == 0:
        create_db()
