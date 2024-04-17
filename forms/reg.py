from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Логин/электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    photo = FileField()
    submit = SubmitField('Зарегистрироваться')