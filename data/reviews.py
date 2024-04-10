import sqlalchemy
from .db_session import SqlAlchemyBase, create_session
from sqlalchemy import orm


class Review(SqlAlchemyBase):
    def __respr__(self):
        db_sess = create_session()
        for user in db_sess.query(Review).all():
            print(user)

    __tablename__ = 'reviews'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    place_name = sqlalchemy.Column(sqlalchemy.String)
    mark = sqlalchemy.Column(sqlalchemy.Integer)
    opinion = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')