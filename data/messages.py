import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                sqlalchemy.ForeignKey("chats.id"))
    sender_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                  sqlalchemy.ForeignKey("users.id"))
    coded_text = sqlalchemy.Column(sqlalchemy.String)
    send_time = sqlalchemy.Column(sqlalchemy.DateTime, 
                                  default=datetime.datetime.now)
    attached_file = sqlalchemy.Column(sqlalchemy.Integer, 
                                  sqlalchemy.ForeignKey("files.id"))
    is_read = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    def code_text(self, text):
        return ''.join([chr(ord(symb) + 19) for symb in text])

    def decode_text(self, text):
        return ''.join([chr(ord(symb) - 19) for symb in text])
