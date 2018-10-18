from flask import render_template, url_for, Blueprint, \
flash, g, request, make_response, redirect, json, jsonify, abort
from flask_login import current_user, login_required
from .. import db, cache
from ..models import News, Category, Product, Page, Comment, Delivery, Order, OrderItem
from ..menu import Menu
from .forms import FormSearch, FormComment, FormAddToCart, FormDelivery
from ..pagination import Paginator
from ..yandex_quickpay import YandexMoney, YandexMoneyHash
from .. import csrf

mod = Blueprint('home', '__name__', url_prefix='', template_folder='app/templates/home')

@cache.cached(timeout=3600, key_prefix='categories')
def get_categories():
    categories_menu = Menu()
    [categories_menu.append(category.title, int(category.id)) for category in Category.query.all()]
    return categories_menu
        
        

@mod.before_request
def before_request():
    # верхнее горизонтальное меню    
    g.menu = Menu()
    g.menu.append('Каталог', url_for('home.catalog'))
    g.menu.append('Способы оплаты', url_for('home.page', alias= 'payment'))
    g.menu.append('Доставка', url_for('home.page', alias= 'delivery'))
    g.menu.append('Контакты', url_for('home.page', alias= 'contact'))
    
    # Меню категорий
    g.categories_menu = get_categories()
    g.category_id = None


    

@mod.route('/')
def home():
    ''' Главная страница '''
    title = 'Интернет магазин'
    news_widget = cache.get('news_widget')
    if not news_widget:
        news_widget = News.query.order_by(db.desc(News.id)).limit(3).all()
        cache.set('news_widget', news_widget)
        
    about = cache.get('about')
    if not about:
        about = Page.query.filter_by(id=1).first()
        cache.set('about', about)
    
    products = cache.get('products')
    if not products:
        products = Product.query.filter_by(best=True).all()
        cache.set('products', products)
    
    form = FormSearch()
    return render_template('index.html',
        title=title,
        news_widget=news_widget,
        about=about,
        products=products,
        form=form)

@mod.route('/search/')
@mod.route('/search/<int:page>/')
def search(page=1):
    ''' Поиск товара '''
    title = 'Поиск по сайту'
    products = []
    pagination=''
    per_page = 30
    form = FormSearch()
    form_add_to_cart = None
    search = request.args.get('search')
    if search:
        form.search.data = search
        search_like = '%{}%'.format(search)
        products_total = Product.query.filter(Product.title.like(search_like)).count()
        paginator = Paginator(per_page, products_total, page)
        pagination = paginator.get_page_links(url_for('home.search'))
        products = Product.query.filter(Product.title.like(search_like)).order_by(db.desc(Product.id)).paginate(per_page=per_page, page=page).items
        form_add_to_cart = FormAddToCart()
        
    return render_template('search.html', title=title, products=products, form=form, form_add_to_cart=form_add_to_cart, pagination=pagination)
    
@mod.route('/catalog/')
@mod.route('/catalog/page/<int:page>/')
def catalog(page=1):
    ''' Список всех товаров '''
    title='Каталог'
    per_page = 20
    total_products = Product.query.filter_by(status=True).count()
    paginator = Paginator(per_page, total_products, page)
    pagination = paginator.get_page_links(url_for('home.catalog'))
    
    products = Product.query.filter_by(status=True).order_by(db.desc(Product.id)).paginate(per_page=per_page, page=page).items
    
    form = FormAddToCart()
   
    return render_template('catalog.html', title=title, products=products, pagination=pagination, form=form)

@mod.route('/catalog/<int:category_id>/')
@mod.route('/catalog/<int:category_id>/<int:page>/')
def catalog_category(category_id=None, page=1):
    ''' Список товаров по категории'''
    category = Category.query.get_or_404(category_id)
    g.category_id = category_id
    title=category.title
    
    per_page = 20
    total_products = category.products.filter_by(status=True).count()
    paginator = Paginator(per_page, total_products, page)
    pagination = paginator.get_page_links(url_for('home.catalog_category', category_id=category_id))
    
    products = category.products.filter_by(status=True).order_by(db.desc(Product.id)).paginate(per_page=per_page, page=page).items
    form = FormAddToCart()
    return render_template('catalog_category.html', title=title, products=products, pagination=pagination, form=form)

@mod.route('/product/<int:product_id>/', methods=['GET','POST'])
@mod.route('/product/<int:category_id>/<int:product_id>/', methods=['GET', 'POST'])
def product(category_id=None, product_id=None):
    product = Product.query.filter_by(id=product_id).first_or_404()
    comments = product.comments.order_by(db.desc(Comment.id))
    g.category_id = category_id
    form = FormComment()
    if form.validate_on_submit() and current_user.is_authenticated:
        db.session.add(Comment(form.text.data, product=product, user=current_user))
        db.session.commit()
        form.text.data = ''
        flash('Ваш комментарий успешно добавлен')
    title = product.title
    form_add_to_cart = FormAddToCart()
    return render_template('product.html',
        title=title,
        product=product,
        comments=comments,
        form=form,
        form_add_to_cart=form_add_to_cart
    )

@mod.route('/news/')
@mod.route('/news/<int:page>/')
def news(page=1):
    ''' Список новостей '''
    title = 'Новости'
    per_page = 20
    total_news = News.query.count()
    paginator = Paginator(per_page, total_news, page)
    pagination = paginator.get_page_links(url_for('home.news'))
    news = News.query.order_by(db.desc(News.id)).paginate(per_page=per_page, page=page).items
    return render_template('news.html', title=title, news=news, pagination=pagination)

@mod.route('/news/get/<int:id>/')
def news_get(id):
    ''' Новость по номеру '''
    news_get = News.query.get_or_404(id)
    title = news_get.title
    return render_template('news_get.html', title=title, news_get=news_get)


@mod.route('/<alias>/')
def page(alias):
    ''' Статические страницы '''
    page = cache.get(alias)
    if not page:
        page = Page.query.filter_by(alias=alias).first_or_404()
        cache.set(alias, page)
    title = page.title
    return render_template('page.html', title=title, page=page)

@mod.route('/cart/')
def cart():
    title = 'Корзина'
    products_loads = json.loads(request.cookies.get('products', '{}')) # список выбранных товаров с куков
    products_ids = list(products_loads.keys())
    products_query = Product.query.filter(Product.id.in_(products_ids)).filter_by(status=True).all()
    return render_template('cart.html',
        title=title,
        products_query=products_query,
        products_loads=products_loads
    )

def count_and_total(products_loads):
    '''Подсчитать общее количество выбранных товаров и полную сумму'''
    products_ids = list(products_loads.keys())
    products_query = Product.query.filter(Product.id.in_(products_ids)).filter_by(status=True).all()
    count = 0
    total = 0
    for item in products_query:
        # Записать количество товаров, если есть в базе и его статус активен
        count = count + products_loads[str(item.id)]
        # Записать также сумму выбранных товаров
        total = total + (products_loads[str(item.id)] * item.cost)
    return count, total

@mod.route('/cart/add/', methods=['POST'])
def cart_add():
    ''' Добавление товара в куки '''
    form = FormAddToCart()
    if form.validate_on_submit():
        product_id = form.product_id.data # номер продукта
        products_loads = json.loads(request.cookies.get('products', '{}')) # список выбранных товаров с куков
        
        if product_id in products_loads:
            # Если есть в куках этот продукт, то добавить еще +1
            products_loads[product_id] += 1
        else:
            # если нету в куках добавить только 1 товар
            products_loads[product_id] = 1
        
        products_dumps = json.dumps(products_loads) #Преобразовать в json для записи в куки
        
        # Колиство выбранных товаров
        # и общая сумма выбранных товаров
        count, total = count_and_total(products_loads)
        
        if request.args.get('html') == '1':
            # ajax запрос
            status = {'status': 'ok', 'product_id': product_id, 'count': count, 'total': '{:,.2f}'.format(total)}
            response = make_response(jsonify(status))
        else:
            # Простой post запрос и редирект обратно на страницу покупки
            response = make_response(redirect(request.referrer))
        
        # Запись количество выбранных товаров и общую сумму в куки
        response.set_cookie('total', str(total))
        response.set_cookie('count', str(count))
        # Запись в куки выбранные товары
        response.set_cookie('products', products_dumps)
        return response
    
    return request.referrer

@mod.route('/cart/delete/<product_id>/')
def cart_delete(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return redirect(url_for('home.cart'))
    products_loads = json.loads(request.cookies.get('products', '{}'))
    
    if product_id in products_loads:
        # Если есть в куках этот продукт, то удалить
        del products_loads[product_id]
    
    # Преобразовать в json список товаров
    products_dumps = json.dumps(products_loads)
    # Колиство выбранных товаров
    # и общая сумма выбранных товаров
    count, total = count_and_total(products_loads)
    
    response = make_response(redirect(url_for('home.cart')))
    # Запись количество выбранных товаров и общую сумму в куки
    response.set_cookie('total', str(total))
    response.set_cookie('count', str(count))
    # Запись в куки выбранные товары
    response.set_cookie('products', products_dumps)
    
    return response

@mod.route('/cart/order/', methods=['GET', 'POST'])
@login_required
def cart_order():
    title = 'Оформление заказа'
    delivery = Delivery.query.order_by(Delivery.cost).all()
    form = FormDelivery()
    form.delivery.choices = [(item.id, item.title) for item in delivery]
    
    if request.method != 'POST':
        form.delivery.data=Delivery.query.order_by(Delivery.cost).first().id
        form.firstname.data=current_user.firstname
        form.lastname.data=current_user.lastname
        form.address.data=current_user.address
    
    if form.validate_on_submit():
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.address = form.address.data
        db.session.commit()
                
        resp = make_response(redirect(url_for('home.cart_payment')))
        resp.set_cookie('delivery', str(form.delivery.data))
        return  resp
    
    return render_template('cart_order.html', title=title, form=form, delivery=delivery)

@mod.route('/cart/payment/')
@login_required
def cart_payment():
    ''' Проверка данных перед оплатой '''
    title = 'Оформление заказа'
    delivery = Delivery.query.filter_by(id=request.cookies.get('delivery')).first()
    products_loads = json.loads(request.cookies.get('products', '{}'))
    count, total = count_and_total(products_loads)
    
    # Проверка если нету в бд доставки и стоимость набранных товаров 0
    # сделать редирект к оформлению заказа
    if not delivery or not total:
        return redirect(url_for('home.cart_order'))
    return render_template('cart_payment.html', title=title, delivery=delivery, total=total)

@mod.route('/payment1/')
@login_required
def payment1():
    ''' Добавление данных в таблицу с заказами'''
    delivery = Delivery.query.filter_by(id=request.cookies.get('delivery')).first()
    
    products_loads = json.loads(request.cookies.get('products', '{}'))
    count, total = count_and_total(products_loads)
    
    # Проверка если нету в бд доставки и стоимость набранных товаров 0
    # сделать редирект к оформлению заказа
    if not delivery or not total:
        return redirect(url_for('home.cart_order'))
    
    # Общая сумма товаров + сумма доставки
    total_sum  = float(total) + float(delivery.cost)
    
    # Запись заказа
    order = Order(
        total_sum=total_sum,
        user=current_user,
        delivery_title=delivery.title,
        delivery_cost=delivery.cost
    )
    
    # Добавить все выбранные товары пользователем
    products_ids = list(products_loads.keys())
    products_query = Product.query.filter(Product.id.in_(products_ids)).filter_by(status=True).all()
    for item in products_query:
        # Записать количество товаров, если есть в базе и его статус активен
        count = products_loads[str(item.id)]
        order.order_items.append(OrderItem(title=item.title, cost=item.cost, count=count))
    
    db.session.add(order)
    db.session.commit()
    
    yandex_money = YandexMoney(order.id, total_sum)
    
    response = make_response(yandex_money.redirect())
    response.set_cookie('products', '', expires=0)
    response.set_cookie('delivery', '', expires=0)
    response.set_cookie('total', '', expires=0)
    response.set_cookie('count', '', expires=0)
    
    return response


@mod.route('/success/')
def success():
    title = 'Спасибо. Ваша заявка успешно оплачена.'
    return render_template('success.html', title=title)
    
@mod.route('/notification/', methods=['POST'])
@csrf.exempt
def notification():
    yandex_money_hash = YandexMoneyHash(request.form)
    
    if not yandex_money_hash.check():
        return abort(400)
    
    order = Order.query.filter_by(id=request.form['label']).first()
    if not order:
        return abort(404)
    
    if float(request.form['withdraw_amount']) == order.total_sum and not order.status_pay:
        order.status_pay = True
        db.session.commit()
        
    return ''