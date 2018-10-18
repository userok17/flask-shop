from flask import Blueprint, redirect, render_template, url_for, request, flash, g, abort
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ..models import User, Category, Role
from .forms import FormLogin, FormRegistration, FormEmail, FormPassword
from ..menu import Menu
from .. import db, app
from ..send_mail import send_mail
from ..decorators import check_authenticated


mod = Blueprint('auth', '__name__', url_prefix='/auth', template_folder='app/templates/auth')


@mod.before_request
def before_request():
    # верхнее горизонтальное меню
    g.menu = Menu()
    g.menu.append('Каталог', url_for('home.catalog'))
    g.menu.append('Способы оплаты', url_for('home.page', alias= 'payment'))
    g.menu.append('Доставка', url_for('home.page', alias= 'delivery'))
    g.menu.append('Контакты', url_for('home.page', alias= 'contact'))
    

@mod.route('/login/', methods=['GET', 'POST'])
@check_authenticated
def login():
    ''' Вход в личный кабинет '''
    title = 'Вход в личный кабинет'
    form = FormLogin()
    if form.validate_on_submit():
        user = User.query.filter(db.or_(User.username==form.login.data, User.email==form.login.data)).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('home.home'))
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', title=title, form=form)

@mod.route('/logout/')
@login_required
def logout():
    ''' Выход из личного кабинета '''
    logout_user()
    return redirect(url_for('home.home'))

@mod.route('/register/', methods=['GET', 'POST'])
@check_authenticated
def register():
    ''' Регистрация '''
    title = 'Регистрация'
    form = FormRegistration()
    if form.validate_on_submit():
        role = Role.query.filter_by(name='login').first()
        user = User(
            username=form.username.data,
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            password=form.password.data,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token('register')
        send_mail(user.email, 'Потвердите ваш e-mail', 'email/email_confirmation_message', user=user, token=token)
        return redirect(url_for('auth.confirm_done'))
    return render_template('register.html', title=title, form=form)

@mod.route('/confirm/done/')
def confirm_done():
    ''' Сообщение, что было отправлено письмо для потверждения учетной записи'''
    title = 'Потвердите ваш e-mail'
    return render_template('confirm_done.html', title=title)

@mod.route('/confirm/<token>/')
def confirm_email(token):
    ''' Потверждение учетной записи '''
    s = Serializer(app.config['SECRET_KEY'])
    # Если нету токена, то вызвать ошибку +1
    try:
        data = s.loads(token)
    except:
        return render_template('confirm_error.html', title='Потвердите ваш email')
    
    
    user = User.query.filter_by(id=data.get('register')).first()
    
    # Если такого пользователя нету вызвать ошибку +2
    if not user:
        return render_template('confirm_error.html', title='Потвердите ваш email')
    
    # Если пользователь потверждал вызвать ошибку +3
    if user.confirmed:
        return render_template('confirm_error.html', title='Потвердите ваш email')
   
    user.confirmed = True
    
    db.session.add(user)
    db.session.commit()
    
    flash('Ваш аккаунт успешно потвержден!', 'success')
    
    return redirect(url_for('auth.login'))
    

@mod.route('/reset/', methods=['GET','POST'])
@check_authenticated
def reset():
    ''' Форма ввод email для сброса пароля '''
    title = 'Cменить пароль'
    form = FormEmail()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('Нет пользователя с таким email ', 'danger')
        else:
            token = user.generate_confirmation_token('reset')
            send_mail(user.email, title, 'email/email_reset_with_token', user=user, token=token)
            return redirect(url_for('auth.reset_done'))
    return render_template('reset.html', title=title, form=form)

@mod.route('/reset/done/')
@check_authenticated
def reset_done():
    ''' Уведомление, что сообщение отправлено на эл. почту для сброса '''
    title = 'Восстановление пароля'
    return render_template('reset_done.html', title=title)

@mod.route('/reset/<token>/', methods=['GET', 'POST'])
@check_authenticated
def reset_with_token(token):
    ''' Новый пароль '''
    s = Serializer(app.config['SECRET_KEY'])
    # если нету токена  показываем ошибку
    try:
        data = s.loads(token)
    except:
        return render_template('reset_error.html', title='Сброс пароля - неправильный ключ')
    form = FormPassword()
    if form.validate_on_submit():
        # если нету пользователя вызвать ошибку
        user = User.query.filter_by(id=data.get('reset')).first()
        if not user:
            return render_template('reset_error.html', title='Сброс пароля - неправильный ключ')
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Пароль успешно изменен! Теперь можете войти в личный кабинет.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_with_token.html', title='Сменить пароль', form=form)


@mod.route('/unconfirmed/')
@login_required
def unconfirmed():
    ''' Сообщение пользователю, что не потвердил учетную запись'''
    title = 'Пожалуйста, подтвердите свою учетную запись'
    return render_template('unconfirmed.html', title=title)

@mod.route('/resend_confirm/')
@login_required
def resend_confirm():
    ''' Отправить заново письмо с подтверждением учетной записи'''
    title = 'Потвердите ваш e-mail'
    user = current_user
    token = user.generate_confirmation_token('register')
    send_mail(user.email,
        'Потвердите ваш e-mail',
        'email/email_confirmation_message',
        user=user,
        token=token
    )
    return redirect(url_for('auth.confirm_done'))
    
