from flask import redirect, url_for
from flask_login import current_user
from functools import wraps


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role.name == 'admin':
            return func(*args, **kwargs)
        else:
            return redirect(url_for('home.home'))
    return wrapper


def check_confirmed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.confirmed is False:
            return redirect(url_for('auth.unconfirmed'))
        return func(*args, **kwargs)
    return wrapper

def check_authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('home.home'))
        return func(*args, **kwargs)
    return wrapper
