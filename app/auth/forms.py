from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, ValidationError
from ..models import User

class FormLogin(Form):
    ''' Форма вход в личный кабинет '''
    login = StringField(label='Логин или Email', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    password = PasswordField(label='Пароль',validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    remember_me = BooleanField(label='Запомнить меня')
    submit = SubmitField(label='Войти')
    
class FormRegistration(Form):
    ''' Форма регистрации'''
    email = StringField(label='Email', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Email(message='Email введен не корректно'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов')
    ])
    username = StringField(label='Логин', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов'),
        validators.Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Логин должен содержать только латинские буквы, цифры, точки или подчеркивания')
    ])
    firstname = StringField(label='Ваше имя', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов')
    ])
    lastname = StringField(label='Ваша фамилия', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов')
    ])
    password = PasswordField(label='Пароль', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.EqualTo('password2', message='Пароли должны совпадать')
    ])
    password2 = PasswordField(label='Повторите пароль', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    submit = SubmitField(label='Зарегистрироваться')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Пользователь с таким email уже зарегистрирован')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Пользователь с таким логином уже зарегистрирован')

class FormEmail(Form):
    email = StringField(label='Email', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Email(message='Email введен не корректно')
    ])
    submit = SubmitField(label='Сбросить мой пароль')
    
class FormPassword(Form):
    password = PasswordField(label='Пароль', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.EqualTo('password2', message='Пароли должны совпадать')
    ])
    password2 = PasswordField(label='Повторите пароль', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    submit = SubmitField(label='Отправить')