import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String)
    bdate = sqlalchemy.Column(sqlalchemy.Date)
    descript = sqlalchemy.Column(sqlalchemy.String)
    friends = sqlalchemy.Column(sqlalchemy.String, default='')
    city = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    last_online = sqlalchemy.Column(sqlalchemy.DateTime,
                                    default=datetime.datetime.now())
    free_chat = sqlalchemy.Column(sqlalchemy.Boolean)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_verified = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_blocked = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    block_reason = sqlalchemy.Column(sqlalchemy.String)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def count_age(self):
        return (datetime.date(year=datetime.datetime.now().year,
                              month=datetime.datetime.now().month,
                              day=datetime.datetime.now().day) - self.bdate).days // 365
