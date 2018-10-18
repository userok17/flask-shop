from flask import render_template, url_for, Blueprint, flash, redirect, request, g
from flask_login import login_required
import os
from ..menu import Menu
from .. import db, app, cache
from ..models import News, Category, Product, Page, User, Delivery, Order
from .forms import FormPost, FormCategory, FormProduct, FormPage, FormSearch, FormDelivery
from ..save_image import SaveImage
from ..pagination import Paginator
from ..decorators import admin_required


mod = Blueprint('admin', '__name__', url_prefix='/admin', template_folder='app/templates/admin')

        
@mod.before_request
def before_request():
    g.menu = Menu()
    g.menu.append('Новости', url_for('admin.news'), url_for('admin.news_add'), '/admin/news/edit/')
    g.menu.append('Страницы', url_for('admin.pages'), '/admin/pages/edit/')
    g.menu.append('Категории товаров', url_for('admin.categories'), url_for('admin.categories_add'), '/admin/categories/edit/')
    g.menu.append('Товары', url_for('admin.products'), url_for('admin.products_add'),'/admin/products_edit/')
    g.menu.append('Доставка', url_for('admin.delivery'), url_for('admin.delivery_add'),'/admin/delivery_edit/')
    g.menu.append('Заказы', url_for('admin.orders'), 'admin.orders_items')
        

@mod.route('/')
@login_required
@admin_required
def admin():    
    title = 'Администраторская часть'
    news_count = News.query.count()
    products_count = Product.query.count()
    buyers_count = User.query.count()
    orders_count = Order.query.count()
    return render_template('admin.html',
        title=title,
        news_count=news_count,
        products_count=products_count,
        buyers_count=buyers_count,
        orders_count=orders_count
    )

@mod.route('/news/')
@mod.route('/news/<int:page>/')
@login_required
@admin_required
def news(page=1):
    title = 'Список новостей'
    per_page = 30
    news_total = News.query.count()
    paginator = Paginator(per_page, news_total, page)
    pagination = paginator.get_page_links(url_for('admin.news'))
    news = News.query.order_by(db.desc(News.id)).paginate(per_page=per_page, page=page).items
    return render_template('news_list.html', title=title, news=news, pagination=pagination)

@mod.route('/news/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def news_add():
    title = 'Добавить новость'
    form = FormPost()
    if form.validate_on_submit():
        db.session.add(News(form.title.data, form.intro.data, form.text.data))
        db.session.commit()
        cache.delete('news_widget')
        flash('Новость "{}" успешно добавлена!'.format(form.title.data))
        return redirect(url_for('admin.news'))
    return render_template('form-post.html', title=title, form=form)

@mod.route('/news/edit/<int:news_id>/', methods=['GET','POST'])
@login_required
@admin_required
def news_edit(news_id):
    news = News.query.filter_by(id=news_id).first()
    if not news:
        return redirect(url_for('admin.news'))
    title = 'Редактировать новость'
    form = FormPost()
    if request.method != 'POST':
        form.title.data = news.title
        form.intro.data = news.intro
        form.text.data = news.text
    if form.validate_on_submit():
        news.title = form.title.data
        news.intro = form.intro.data
        news.text = form.text.data

        db.session.commit()
        cache.delete('news_widget')
        flash('Новость "{}" успешно изменена'.format(form.title.data))
        return redirect(url_for('admin.news'))
    return render_template('form-post.html', title=title, form=form)

@mod.route('/news/delete/<int:news_id>/')
@login_required
@admin_required
def news_delete(news_id):
    news = News.query.filter_by(id=news_id).first()
    if not news:
        return redirect(url_for('admin.news'))
    News.query.filter_by(id=news_id).delete()
    db.session.commit()
    cache.delete('news_widget')
    flash('Новость "{}" успешно удалена!'.format(news.title))
    return redirect(url_for('admin.news'))


@mod.route('/categories/')
@login_required
@admin_required
def categories():
    title = 'Категории'
    categories = Category.query.all()
    return render_template('categories_list.html', title=title, categories=categories)

@mod.route('/categories/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def categories_add():
    title = 'Добавить категорию'
    form = FormCategory()
    if form.validate_on_submit():
        db.session.add(Category(title=form.title.data))
        db.session.commit()
        cache.delete('categories')
        flash('Категория "{}" успешно добавлена!'.format(form.title.data))
        return redirect(url_for('admin.categories'))    
    return render_template('form-post.html', title=title, form=form)

@mod.route('/categories/edit/<int:category_id>/', methods=['GET','POST'])
@login_required
@admin_required
def categories_edit(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return redirect(url_for('admin.categories'))
    title = 'Редактирование категории'
    form = FormCategory()
    if request.method != 'POST':
        form.title.data = category.title
    if form.validate_on_submit():
        category.title = form.title.data
        db.session.commit()
        cache.delete('categories')
        flash('Категория "{}" успешно изменена!'.format(form.title.data))
        return redirect(url_for('admin.categories'))
    return render_template('form-post.html', title=title, form=form)

@mod.route('/categories/delete/<int:category_id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def categories_delete(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if not category:
        return redirect(url_for('admin.categories'))
    Category.query.filter_by(id=category_id).delete()
    db.session.commit()
    cache.delete('categories')
    flash('Категория "{}" успешно удалена!'.format(category.title))
    return redirect(url_for('admin.categories'))

@mod.route('/products/')
@mod.route('/products/<int:page>/')
@login_required
@admin_required
def products(page=1):
    title = 'Список товаров'
    per_page = 30
    
    form = FormSearch()
    search = request.args.get('search')
    if search:
        form.search.data = search
        search_like = '%{}%'.format(search)
        products_total = Product.query.filter(Product.title.like(search_like)).count()
        paginator = Paginator(per_page, products_total, page)
        pagination = paginator.get_page_links(url_for('admin.products'))
        products = Product.query.filter(Product.title.like(search_like)).order_by(db.desc(Product.id)).paginate(per_page=per_page, page=page).items
    else:
        products_total = Product.query.count()
        paginator = Paginator(per_page, products_total, page)
        pagination = paginator.get_page_links(url_for('admin.products'))
        products = Product.query.order_by(db.desc(Product.id)).paginate(per_page=per_page, page=page).items
    return render_template('products_list.html', title=title, products=products, pagination=pagination, form=form)

@mod.route('/products/add/', methods=['GET','POST'])
@login_required
@admin_required
def products_add():
    title = 'Добавить товар'
    form = FormProduct()
    form.categories.choices = [(category.id, category.title) for category in Category.query.all()]
    if form.validate_on_submit():
        product = Product(form.title.data, form.description.data, form.cost.data, form.best.data, form.status.data)
        if form.image.data:
            image = SaveImage(form.image.data.stream, app.config['UPLOAD_PATH'])
            image.resize(height=240, auto_resize=True)
            image.save()
            product.image = image.filename
        for category_id in form.categories.data:
            product.categories.append(Category.query.filter_by(id=category_id).first())
        db.session.commit()
        cache.delete('products')
        flash('Товар "{}" успешно добавлен!'.format(form.title.data))
        return redirect(url_for('admin.products'))
    return render_template('form-post.html', title='Добавить товар', form=form)

@mod.route('/products/edit/<int:product_id>/', methods=['GET','POST'])
@login_required
@admin_required
def products_edit(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return redirect(url_for('admin.products'))
    title = 'Редактировать товар'
    
    form = FormProduct()
    form.categories.choices = [(category.id, category.title) for category in Category.query.all()]
    if request.method != 'POST':
        form.title.data = product.title
        form.description.data = product.description
        form.cost.data = product.cost
        form.status.data = product.status
        form.best.data = product.best
        form.categories.data = [category.id for category in product.categories]
    if form.validate_on_submit():
        if form.image.data:
            filename = product.image
            image = SaveImage(form.image.data.stream, app.config['UPLOAD_PATH'], filename)
            image.resize(height=240, auto_resize=True)
            image.save()
            product.image = image.filename
        product.title = form.title.data
        product.description = form.description.data
        product.cost = form.cost.data
        product.best = form.best.data
        product.status = form.status.data
        product.categories = []
        for category_id in form.categories.data:
            product.categories.append(Category.query.get(category_id))
        db.session.commit()
        cache.delete('products')
        flash('Товар {} успешно изменен!'.format(form.title.data))
        return redirect(url_for('admin.products'))
    return render_template('form-post-product-edit.html', title=title, form=form, product=product)
    
@mod.route('/products/delete/<int:product_id>/')
@login_required
@admin_required
def products_delete(product_id):
    ''' Удаление товара '''
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return redirect(url_for('admin.products'))
    try:
        os.unlink(os.path.join(app.config['UPLOAD_PATH'], product.image))
    except FileNotFoundError:
        pass
    Product.query.filter_by(id=product_id).delete()
    db.session.commit()
    cache.delete('products')
    flash('Товар {} успешно удален!'.format(product.title))
    return redirect(url_for('admin.products'))

@mod.route('/pages/')
@login_required
@admin_required
def pages():
    title = 'Список страниц'
    pages = Page.query.all()
    return render_template('pages_list.html', title=title, pages=pages)


@mod.route('/pages/edit/<int:page_id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def pages_edit(page_id):
    page = Page.query.filter_by(id=page_id).first()
    if not page:
        return redirect(url_for('admin.pages'))
    title = page.title
    form = FormPage()
    if request.method != 'POST':
        form.text.data = page.text
    if form.validate_on_submit():
        page.text = form.text.data

        db.session.commit()
        cache.delete(page.alias)
        flash('Страница "{}" успешно изменена'.format(page.title))
        return redirect(url_for('admin.pages'))
    return render_template('form-post.html', title=title, form=form)

@mod.route('/delivery/')
def delivery():
    title = 'Доставка'
    delivery_list = Delivery.query.order_by(Delivery.cost).all()
    return render_template('delivery_list.html', title=title, delivery_list=delivery_list)

@mod.route('/delivery/add/', methods=['GET','POST'])
def delivery_add():
    title = 'Добавить доставку'
    form = FormDelivery()
    if form.validate_on_submit():
        db.session.add(Delivery(form.title.data, form.description.data, form.cost.data, form.status.data))
        db.session.commit()
        flash('Новая запись "{}" успешно добавлена'.format(form.title.data))
        return redirect(url_for('admin.delivery'))
    return render_template('form-post.html', title=title, form=form)

@mod.route('/delivery/edit/<int:delivery_id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def delivery_edit(delivery_id):
    delivery = Delivery.query.filter_by(id=delivery_id).first()
    if not delivery:
        return redirect(url_for('admin.delivery'))
    title = delivery.title
    form = FormDelivery()
    if request.method != 'POST':
        form.title.data = delivery.title
        form.description.data = delivery.description
        form.cost.data = delivery.cost
        form.status.data = delivery.status
    
    if form.validate_on_submit():
        delivery.title = form.title.data
        delivery.description = form.description.data
        delivery.cost = form.cost.data
        delivery.status = form.status.data
        db.session.commit()
        flash('Запись "{}" успешно изменена!'.format(delivery.title))
        return redirect(url_for('admin.delivery'))
    return render_template('form-post.html', title=title, form=form)

@mod.route('/delivery/delete/<int:delivery_id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def delivery_delete(delivery_id):
    delivery = Delivery.query.filter_by(id=delivery_id).first()
    if not delivery:
        return redirect(url_for('admin.delivery'))
    Delivery.query.filter_by(id=delivery_id).delete()
    db.session.commit()
    flash('Запись "{}" успешна удалена!'.format(delivery.title))
    return redirect(url_for('admin.delivery'))

@mod.route('/orders/')
@login_required
@admin_required
def orders():
    title = 'Список заказов'
    orders = Order.query.order_by(db.desc(Order.id)).all()
    return render_template('orders_list.html', title=title, orders=orders)

@mod.route('/orders/items/<int:order_id>/')
@login_required
@admin_required
def orders_items(order_id):
    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return redirect(url_for('cabinet.orders'))
    title = 'Идентификатор заказа №{}'.format(order.id)
    return render_template('orders_items_list.html', title=title, order=order)

