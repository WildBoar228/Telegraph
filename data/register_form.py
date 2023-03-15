from flask_login import LoginManager, current_user
from flask_wtf import FlaskForm
from wtforms import (EmailField, PasswordField, StringField,IntegerField, SubmitField,
                     DateField, TextAreaField)
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    surname = StringField('Фамилия *', validators=[DataRequired()])
    name = StringField('Имя *', validators=[DataRequired()])
    bdate = DateField('Дата рождения')
    descript = TextAreaField('Расскажите о себе')
    city = StringField('Ваш город')
    email = EmailField('Почта или номер телефона *', validators=[DataRequired()])
    password = PasswordField('Пароль *', validators=[DataRequired()])
    password2 = PasswordField('Подтвердите пароль *', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
