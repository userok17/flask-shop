#!/usr/bin/env python3
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_cache import Cache
from .filters import *
#from werkzeug.contrib.profiler import ProfilerMiddleware


app = Flask(__name__)



#app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('flask_tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    


csrf = CsrfProtect(app)

Bootstrap(app)

cache = Cache()
cache.init_app(app)


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, введите логин и пароль, чтобы получить доступ к этой странице.'
login_manager.init_app(app)


app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['strftime'] = strftime_filter
app.jinja_env.filters['format_currency'] = format_currency

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


from .home.views import mod
app.register_blueprint(mod)
from .admin.views import mod
app.register_blueprint(mod)
from .auth.views import mod
app.register_blueprint(mod)
from .cabinet.views import mod
app.register_blueprint(mod)