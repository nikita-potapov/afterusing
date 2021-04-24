import datetime

import hashlib
import os

from PIL import Image

from flask import Flask, redirect, render_template, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api

from data import db_session
from data.products import Product
from data.users import User
from forms.product import AddProductForm
from forms.user import RegisterForm, LoginForm

from settings import *

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def save_image_and_get_path(req):
    img_container = req.files['image']
    filename = img_container.filename.replace(' ', '_')
    saved_date_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
    end_of_filename = '_'.join([saved_date_time, str(filename)])
    hashing_str = str(current_user.id) + end_of_filename
    temp = hashlib.sha1(hashing_str.encode('utf-8')).hexdigest() + '_' + end_of_filename
    norm_path = os.path.normpath(PRODUCT_IMG_PATH)
    temp = os.path.normpath(temp)
    product_img_path = os.path.join(norm_path, temp)

    img_container.save(product_img_path)
    picture = Image.open(product_img_path)
    picture.save(product_img_path, optimize=True, quality=30)
    return '/' + product_img_path


def main():
    db_session.global_init('db/database.db')
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port)


@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        db_sess = db_session.create_session()
        search_phrase = request.args.get('q')
        if search_phrase:
            products = db_sess.query(Product).filter(
                (Product.low_title.contains(search_phrase)) | (
                    Product.low_content.contains(search_phrase))).all()
        else:
            products = db_sess.query(Product).all()

        products = sorted(products, key=lambda x: x.created_date, reverse=True)
        for i in range(len(products)):
            if products[i].path_to_img is None:
                products[i].path_to_img = os.path.join(PRODUCT_IMG_PATH, 'no_photo.png')
        params = {
            'title': 'Все объявления',
            'products': products,
        }
        return render_template('index.html', **params)
    elif request.method == 'POST':
        return 'POST METHOD'


@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():

        if form.image.data:
            product_img_path = save_image_and_get_path(request)
        else:
            product_img_path = None

        db_sess = db_session.create_session()
        product = Product(
            user_id=current_user.id,
            cost=form.cost.data,
            title=form.title.data,
            content=form.content.data,
            created_date=datetime.datetime.now(),
            path_to_img=product_img_path,
            contact_number=form.contact_number.data
        )
        product.reinitialized_indexes()
        db_sess.add(product)
        db_sess.commit()
        return redirect('/')
    return render_template('add_product.html',
                           title='Добавление объявления',
                           form=form)


@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    form = AddProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id,
                                                Product.user_id == current_user.id).first()
        if product:
            form.cost.data = product.cost
            form.title.data = product.title
            form.content.data = product.content
            form.contact_number.data = product.contact_number

        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id,
                                                Product.user_id == current_user.id).first()
        if product:
            product.cost = form.cost.data
            product.title = form.title.data
            product.content = form.content.data
            if form.image.data:
                product_img_path = save_image_and_get_path(request)
                product.path_to_img = product_img_path

            product.created_date = datetime.datetime.now()

            product.reinitialized_indexes()
            db_sess.commit()
            return redirect('/my_products')
        else:
            abort(404)
    return render_template('add_product.html',
                           title='Редактирование объявления',
                           form=form
                           )


@app.route('/delete_product/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_product(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id,
                                            Product.user_id == current_user.id).first()
    if product:
        if product.path_to_img:
            try:
                os.remove(product.path_to_img)
            except Exception:
                pass
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(403)
    return redirect('/my_products')


@app.route('/product_details/<int:id>', methods=['GET', 'POST'])
def product_details(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    if product:
        params = {
            'title': product.title,
            'product': product
        }
        return render_template('product_details.html', **params)
    else:
        return abort(404)


@app.route('/my_products', methods=['GET', 'POST'])
@login_required
def my_products():
    db_sess = db_session.create_session()
    search_phrase = request.args.get('q')
    if search_phrase:
        search_phrase = search_phrase.lower().strip()
        products = db_sess.query(Product).filter(
            ((Product.low_title.contains(search_phrase)) | (
                Product.low_content.contains(search_phrase))),
            (Product.user_id == current_user.id)).all()
    else:
        products = db_sess.query(Product).filter(Product.user_id == current_user.id).all()
    products = sorted(products, key=lambda x: x.created_date, reverse=True)
    for i in range(len(products)):
        if products[i].path_to_img is None:
            products[i].path_to_img = os.path.join(PRODUCT_IMG_PATH, 'no_photo.png')
    params = {
        'title': 'Мои объявления',
        'can_edit': True
    }
    if products:
        params['products'] = products
        return render_template('index.html', **params)
    else:
        return render_template('user_have_not_products.html', **params)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    params = {
        'title': 'Oops! Server ...',
        'error_number': '404',
        'error_message': 'Oops! The page you requested was not found.'
    }
    return render_template('error_template.html', **params)


@app.errorhandler(500)
def server_not_responded(error):
    params = {
        'title': 'Oops! Server ...',
        'error_number': '500',
        'error_message': 'Sorry, but our server is lying down to rest...'
    }
    return render_template('error_template.html', **params)


@app.errorhandler(401)
def not_authenticated(error):
    return redirect('/login')


if __name__ == '__main__':
    main()
