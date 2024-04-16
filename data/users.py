import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase, create_session
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    def __repr__(self):
        db_sess = create_session()
        for user in db_sess.query(User).all():
            print(user)

    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String)
    review = orm.relationship("Review", back_populates='user')

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password