import sqlalchemy
from .db_session import SqlAlchemyBase, create_session


class User(SqlAlchemyBase):
    def __repr__(self):
        db_sess = create_session()
        for user in db_sess.query(User).all():
            print(user)

    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)