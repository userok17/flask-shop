from flask_wtf import Form,  RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, FloatField, BooleanField, SelectMultipleField, SubmitField, validators
from werkzeug import secure_filename
import re


class FormPost(Form):
    '''Форма Добавление новостей или статей '''    
    title = StringField(label='Заголовок', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=255, message='Поле не должно превышать более %(max)s символов')
    ])
    intro = TextAreaField(label='Короткое описание', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=255, message='Поле не должно превышать более %(max)s символов')
    ])
    text = TextAreaField(label='Текст', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
    ])
    submit = SubmitField('Сохранить')

class FormCategory(Form):
    ''' Форма Добавление категории '''
    title = StringField(label='Название категории', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=255, message='Поле не должно превышать более %(max)s символов')
    ])
    submit = SubmitField('Сохранить')

class FormProduct(Form):
    ''' Форма Добавление товара '''
    title = StringField(label='Наименование товара', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=255, message='Поле не должно превышать более %(max)s символов')
    ])
    categories = SelectMultipleField(label='Категории', coerce=int, validators=[
        validators.Required(message='Выберете категорию')
    ])
    description = TextAreaField(label='Описание товара', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    image = FileField(label='Изображение', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Файл для загрузки могут быть только .jpg, .jpeg, png')
    ])
    cost = FloatField(label='Стоимость товара', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    best = BooleanField(label='Лучший товар')
    status = BooleanField(label='Активен')
    submit = SubmitField(label='Сохранить')
    
    
class FormPage(Form):
    ''' Форма редактирование страниц '''
    text = TextAreaField(label='Текст', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    submit = SubmitField(label='Сохранить')
    
class FormSearch(Form):
    ''' Поиск товара '''
    search = StringField(render_kw={'placeholder':'Введите наименование товара',
        'class':'form-control'}, validators=[
        validators.Required()
    ])
    submit = SubmitField('Искать', render_kw={'class':'btn btn-default'})
    
class FormDelivery(Form):
    ''' Доставка '''
    title = StringField(label='Заголовок', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=255, message='Поле не должно превышать более %(max)s символов')
    ])
    description = TextAreaField(label='Описание', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    cost = FloatField(label='Стоимость доставки', default=0)
    status = BooleanField(label='Активен')
    submit = SubmitField('Сохранить')
