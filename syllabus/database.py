import os

import binascii
import re
import stat
from operator import or_

from sqlalchemy import create_engine, text
from sqlalchemy.engine import ResultProxy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from syllabus import get_root_path
from syllabus import get_config

database_uri = os.environ.get("SYLLABUS_DATABASE_URI", 'sqlite:///%s' % os.path.join(get_root_path(), 'database.sqlite'))
engine = create_engine(database_uri)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

current_version = 4


def create_db_user():
    from syllabus.models.user import User
    change_pwd_bytes = os.urandom(20)
    change_pwd_hex = binascii.hexlify(change_pwd_bytes).decode()
    u = User('admin@localhost', hash_password=None, change_password_url=change_pwd_hex, right='admin',
             activated=True)
    db_session.add(u)
    db_session.commit()
    connection = engine.connect()
    connection.execute(text("PRAGMA main.user_version=%d;" % current_version))


def generate_github_hook():
    from syllabus.models.params import Params
    params = Params.query.first()
    if params is None or params.git_hook_url is None:
        hook_address = os.urandom(20)
        hook_address_hex = binascii.hexlify(hook_address).decode()
        if params is None:
            params = Params(hook_address_hex)
            db_session.add(params)
        else:
            params.git_hook_url = hook_address_hex
        db_session.commit()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import syllabus.models.user
    import syllabus.models.params

    if "sqlite://" in database_uri and not os.path.isfile(database_uri.replace("sqlite://", "")):
        print("Init the database.")
    Base.metadata.create_all(bind=engine)
    from syllabus.models.user import User
    users = User.query.all()
    if len(users) == 0:
        create_db_user()
    admin = User.query.filter(User.email == "admin@localhost").first()
    if admin is not None and admin.hash_password is None:
        print("Go to the following link to reset the admin user password: /resetpassword/%s" % admin.change_password_url)
    
    generate_github_hook()


def reload_database():
    # FIXME: ugly
    global engine, db_session
    engine = create_engine(database_uri, convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))


def update_database():
    if "sqlite" not in database_uri:
        return
    database_path = database_uri.replace("sqlite://", "")
    if os.path.isfile(database_path):
        connection = engine.connect()
        version = connection.execute(text("PRAGMA main.user_version;")).first()[0]
        if version < current_version:
            print("database version (%d) is outdated, updating database to version %d" % (version, current_version))
        if version < 1:
            print("updating to version 1")
            connection.execute(text("ALTER TABLE users ADD COLUMN right STRING(30);"))
        if version < 2:
            print("updating to version 2")
            connection.execute(text("""
            CREATE TABLE params(
               git_hook_url STRING(80),
               id           INTEGER PRIMARY KEY
            );
            """))
            connection.execute(text("""
            INSERT INTO params (git_hook_url, id)
            VALUES (NULL, 1);
            """))
        if version < 3:
            print("updating to version 3")
            # Rename users to users_old and drop index
            connection.execute(text("ALTER TABLE users RENAME TO users_old"))
            connection.execute(text("DROP INDEX ix_users_username"))

            connection.execute(text("""
            CREATE TABLE users (
                username VARCHAR(40) PRIMARY KEY NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                full_name VARCHAR(50),
                hash_password VARCHAR(80),
                change_password_url VARCHAR(50),
                "right" VARCHAR(30),
                activated BOOLEAN NOT NULL
            );
            """))
            connection.execute(text("CREATE INDEX ix_users_username ON users (username)"))

            for row in connection.execute(text("SELECT username, email, full_name, hash_password, change_password_url, "
                                          "right FROM users_old")):
                connection.execute(text("INSERT INTO users (username, email, full_name, hash_password, change_password_url, right, activated) "
                                   "VALUES ('{}', '{}', {}, '{}', {}, {}, {})".format(row[0], row[1], "NULL" if row[2] is None else "'%s'" % row[2],
                                                                                      row[3], "NULL" if row[4] is None else "'%s'" % row[4],
                                                                                      "NULL" if row[5] is None else "'%s'" % row[5], 1)))
            connection.execute(text("DROP TABLE users_old"))
        if version < 4:
            print("updating to version 4")
            from sqlalchemy.schema import CreateTable, CreateIndex
            from syllabus.models.user import User
            connection.execute(text("ALTER TABLE users RENAME TO users_old"))
            connection.execute(text("DROP INDEX ix_users_username"))
            connection.execute(CreateTable(User.__table__))
            for idx in User.__table__.indexes:
                connection.execute(CreateIndex(idx))
            for row in connection.execute(text("SELECT username, email, full_name, hash_password, change_password_url, "
                                          "right, activated FROM users_old")):
                connection.execute(text("INSERT INTO users (email, full_name, hash_password, change_password_url, right, activated) "\
                                       "VALUES ('{}', {}, {}, {}, {}, {})".format(row[1],
                                                                                  "null" if row[2] is None else "'%s'" % row[2],
                                                                                  "null" if row[3] is None else "'%s'" % row[3],
                                                                                  "null" if row[4] is None else "'%s'" % row[4],
                                                                                  "null" if row[5] is None else "'%s'" % row[5],
                                                                                  row[6])))
            connection.execute(text("DROP TABLE users_old"))

        connection.execute(text("PRAGMA main.user_version=%d;" % current_version))
    else:
        print("The database does not exist yet.")


# we cannot register locally if either somebody has the same e-mail
def locally_register_new_user(user, activated=False):
    from syllabus.models.user import User, UserAlreadyExists
    user.activated = activated
    user.right = None
    existing_user = User.query.filter(User.email == user.email).first()
    if existing_user is not None:
        exception = UserAlreadyExists("tried to create user {} while user {} already exists".format(user.to_dict,
                                                                                              existing_user.to_dict()))
        raise exception
    db_session.add(user)
    db_session.commit()

