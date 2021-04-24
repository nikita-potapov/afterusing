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

    is_showing_by_user = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_showing_by_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    low_title = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
    low_content = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f"<Product> {self.id} created {self.created_date}"

    def reinitialized_indexes(self):
        self.low_title = self.title.lower()
        self.low_content = self.content.lower()
