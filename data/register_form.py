from flask_login import LoginManager, current_user
from flask_wtf import FlaskForm
from wtforms import (EmailField, PasswordField, StringField,IntegerField, SubmitField,
                     DateField, TextAreaField, BooleanField)
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Логин (электронная почта) *', validators=[DataRequired()])
    username = StringField('Имя пользователя *', validators=[DataRequired()])
    bdate = DateField('Дата рождения')
    descript = TextAreaField('Расскажите о себе')
    city = StringField('Ваш город')
    password = PasswordField('Пароль *', validators=[DataRequired()])
    password2 = PasswordField('Подтвердите пароль *', validators=[DataRequired()])
    free_chat = BooleanField('Смогут ли вам отправлять сообщения посторонние люди?')
    submit = SubmitField('Зарегистрироваться')
