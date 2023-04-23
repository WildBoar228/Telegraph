from flask_login import LoginManager, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class FriendshipForm(FlaskForm):
    text = TextAreaField('')
    submit = SubmitField('Отправить запрос')
