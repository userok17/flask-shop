from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, validators


class FormProfile(Form):
    firstname = StringField(label='Ваше имя', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов')
    ])
    lastname = StringField(label='Ваша фамилия', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов')
    ])
    email = StringField(label='Email', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Email(message='Email введен не корректно'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов')
    ])
    address = TextAreaField(label='Адрес', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    submit = SubmitField(label='Сохранить')