from flask_wtf import Form
from wtforms import StringField, TextAreaField, IntegerField,  SubmitField, HiddenField,\
RadioField, validators, ValidationError

class FormSearch(Form):
    ''' Поиск по сайту '''
    search = StringField(render_kw={'placeholder':'Введите наименование товара',
        'class':'form-control'}, validators=[
        validators.Required()
    ])
    submit = SubmitField('Искать', render_kw={'class':'btn btn-default'})

class FormComment(Form):
    ''' Комментарий к продукту '''
    text = TextAreaField(label='Ваш комментарий', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    submit = SubmitField(label='Отправить')
    
class FormAddToCart(Form):
    ''' Добавить товар в корзину '''
    product_id = HiddenField()
    submit = SubmitField(label='В корзину')
    
    def validate_product_id(self, field):
        if not field.data.isdigit():
            raise ValidationError('Это поле должен состоять из цифр')
        
class FormDelivery(Form):
    ''' Форма способо доставки '''
    delivery = RadioField(label='Способ доставки', coerce=int, validators=[
        validators.Required(message='Выберете один из способов оплаты')
    ])
    firstname = StringField(label='Ваше имя', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов')
    ])
    lastname = StringField(label='Ваша фамилия', validators=[
        validators.Required(message='Это поле необходимо заполнить'),
        validators.Length(max=64, message='Поле не должно превышать более %(max)s символов')
    ])
    address = TextAreaField(label='Адрес', validators=[
        validators.Required(message='Это поле необходимо заполнить')
    ])
    submit = SubmitField('Перейти к оплате')
        

    