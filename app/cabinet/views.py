from flask import Blueprint, render_template, g, url_for, request, redirect, flash
from flask_login import current_user, login_required
from functools import reduce
from ..menu import Menu
from .forms import FormProfile
from .. import db
from ..decorators import check_confirmed
from ..models import Order
from ..yandex_quickpay import YandexMoney

mod = Blueprint('cabinet', '__name__', url_prefix='/cabinet', template_folder='app/templates/cabinet/')

@mod.before_request
def before_request():
    # верхнее горизонтальное меню
    g.menu = Menu()
    g.menu.append('Каталог', url_for('home.catalog'))
    g.menu.append('Способы оплаты', url_for('home.page', alias= 'payment'))
    g.menu.append('Доставка', url_for('home.page', alias= 'delivery'))
    g.menu.append('Контакты', url_for('home.page', alias= 'contact'))

@mod.route('/')
@login_required
@check_confirmed
def cabinet():
    title = 'Личный кабинет'
    return render_template('cabinet.html', title=title)

@mod.route('/profile/')
@login_required
@check_confirmed
def profile():
    '''Показать данные профиля'''
    title = 'Мой профиль'
    return render_template('profile.html', title=title)

@mod.route('/profile/edit/', methods=['GET', 'POST'])
@login_required
@check_confirmed
def profile_edit():
    '''Редактировать профиль'''
    title = 'Мой профиль'
    form = FormProfile()
    if request.method != 'POST':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email
        form.address.data = current_user.address
    if form.validate_on_submit():
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        db.session.commit()
        flash('Ваш профиль успешно изменен!')
        return redirect(url_for('cabinet.profile'))
    return render_template('profile_edit.html', title=title, form=form)

@mod.route('/orders/')
@login_required
@check_confirmed
def orders():
    title = 'Список заказов'
    orders = Order.query.filter_by(user=current_user).order_by(db.desc(Order.id)).all()
    return render_template('orders.html', title=title, orders=orders)

@mod.route('/orders/items/<int:order_id>/')
@login_required
@check_confirmed
def orders_items(order_id):
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return redirect(url_for('cabinet.orders'))
    title = 'Номер заказа №{}'.format(order.id)
    return render_template('orders_items.html', title=title, order=order)

@mod.route('/orders/payment/<int:order_id>/')
@login_required
@check_confirmed
def orders_payment(order_id):
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return redirect(url_for('cabinet.orders'))
        
    yandex_money = YandexMoney(order.id, order.total_sum)
    
    return yandex_money.redirect()
