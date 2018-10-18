import os
basedir = os.path.dirname(__file__)
DEBUG = True
SECRET_KEY = '#Yfd#$#sDJFKDJJKHJdsjfoijsdif'

# База данных
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@server/db'
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 5 # Количество соединений
SQLALCHEMY_POOL_TIMEOUT = 20
SQLALCHEMY_POOL_RECYCLE = 599

# Почта
MAIL_SERVER = '1rpi.ru'
MAIL_PORT = 587
MAIL_USERNAME ='info@flask-shop7.1rpi.ru'
MAIL_PASSWORD = 'your-password'

FLASKY_MAIL_SUBJECT_PREFIX = 'Интернет-магазин'

FLASKY_FROM = 'info@flask-shop7.1rpi.ru'
FLASKY_FROM_NAME = 'Интернет-магазин'


# Путь куда загружать изображения
UPLOAD_PATH = os.path.join(basedir, 'app', 'static', 'upload')

# Кеширование
CACHE_DEFAULT_TIMEOUT = 31536000
CACHE_TYPE = 'filesystem'
CACHE_DIR = 'cache_filesystem'


#yandex money
YANDEX_MONEY_RECEIVER = 'Номер кошелька'
YANDEX_MONEY_QUICKPAY_FORM = 'shop'
YANDEX_MONEY_SUCCESS_URL = 'http://flask-shop7.1rpi.ru/success/'
YANDEX_MONEY_FORMCOMMENT = 'Интернет магазин'
YANDEX_MONEY_SHORT_DEST = 'Интернет магазин'
YANDEX_MONEY_TARGETS = 'Оплата заказа'
YANDEX_MONEY_PAYMENT_TYPE = 'PC'

YANDEX_MONEY_HASH_SECRET = ''
