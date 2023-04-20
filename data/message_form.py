from flask_login import LoginManager, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    text = TextAreaField('')
    file = FileField('Выберите файл')
    send = SubmitField('Отправить сообщение')
