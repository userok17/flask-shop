from . import db, login_manager, app
from datetime import datetime
from pytz import timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def get_datetime(timezone_value='Europe/Moscow'):
    return datetime.now(timezone(timezone_value))

class News(db.Model):
    ''' Новости '''
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    intro = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, title, intro, text):
        self.title = title
        self.intro = intro
        self.text = text
        self.date_added = get_datetime()

product_in_categories = db.Table('product_in_categories',
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE')),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'))
)
        
class Category(db.Model):
    ''' Категории товаров '''
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    products = db.relationship('Product',
        secondary=product_in_categories,
        backref=db.backref('categories', lazy='dynamic', passive_deletes=True),
        lazy='dynamic',
        passive_deletes=True
    )
    
    def __init__(self, title=title):
        self.title = title

class Product(db.Model):
    ''' Товары '''
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Float(precision='7,2'), nullable=False)
    image = db.Column(db.String(255))
    status = db.Column(db.Boolean, nullable=False, default=False)
    best = db.Column(db.Boolean, nullable=False, default=False)
    comments = db.relationship('Comment', backref='product', lazy='dynamic', cascade='all,delete')
    
    
    def __init__(self, title, description, cost, best, status):
        self.title = title
        self.description = description
        self.cost = cost
        self.best = best
        self.status = status

class Comment(db.Model):
    ''' Комментарии к товару '''
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    datetime_added = db.Column(db.DateTime, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', lazy='joined')
    
    def __init__(self, text, **kwargs):
        self.text = text
        self.datetime_added = get_datetime()
        super().__init__(**kwargs)
        
class Page(db.Model):
    ''' Страницы '''
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    alias= db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    

class Delivery(db.Model):
    ''' Стоимость каждой доставки '''
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Float(precision='7,2'), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)
    
    def __init__(self, title=title, description=description, cost=cost, status=status):
        self.title = title
        self.description = description
        self.cost = cost
        self.status= status
        


class Order(db.Model):
    ''' Заказ товаров '''
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'))
    total_sum = db.Column(db.Float(precision='7,2'), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False)
    status_pay = db.Column(db.Boolean, default=False)
    user = db.relationship('User', lazy='joined')
    delivery_title = db.Column(db.String(255), nullable=False)
    delivery_cost = db.Column(db.Float(precision='7,2'), nullable=False)
    order_items = db.relationship('OrderItem', lazy='dynamic', cascade='all,delete')
    def __init__(self, **kwargs):
        self.date_added = get_datetime()
        super().__init__(**kwargs)
        
class OrderItem(db.Model):
    ''' Список  выбранных товаров'''
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    title = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Float(precision='7,2'), nullable=False)
    count = db.Column(db.Integer, default=1)
    
    def total_sum(self):
        return self.cost * self.count
    
   


class Role(db.Model):
    ''' Права доступа для пользователей '''
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))
    users = db.relationship('User', backref='role', lazy='dynamic')
    
class User(UserMixin, db.Model):
    ''' Пользователи '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    address = db.Column(db.Text)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    @property
    def password():
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_confirmation_token(self, key, expiration=86400):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({key: self.id})
    
        
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))