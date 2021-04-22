import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relation('User')

    path_to_img = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    contact_number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime)

    def __repr__(self):
        return f"<Product> {self.id} created {self.created_date}"
