import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Chat(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    collaborators = sqlalchemy.Column(sqlalchemy.String)
    messages = sqlalchemy.Column(sqlalchemy.String, nullable=True)
