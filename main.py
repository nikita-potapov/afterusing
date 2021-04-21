from flask import Flask, redirect, render_template, request, abort, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api

from data import db_session
from data.products import Product
from data.users import User
from forms.product import AddProductForm
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init('db/database.db')
    app.run(port=8080, host='127.0.0.1')


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    if request.method == 'GET':
        db_sess = db_session.create_session()
        products = db_sess.query(Product).all()
        params = {
            'title': 'Все объявления',
            'products': products
        }
        return render_template('index.html', **params)
    elif request.method == 'POST':
        return 'POST METHOD'


@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = Product(
            user_id=current_user.id,
            cost=form.cost.data,
            title=form.title.data,
            content=form.content.data
        )
        db_sess.add(product)
        db_sess.commit()
        return redirect('/')
    return render_template('add_product.html',
                           title='Добавление объявления',
                           form=form)


@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = AddProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id,
                                                Product.user_id == current_user.id).first()
        if product:
            form.team_leader.data = product.team_leader

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
            product.image = form.image.data

            db_sess.commit()
            return redirect('/')
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
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(403)
    return redirect('/')


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
    return make_response(jsonify({'message': 'Not found'}), 404)


if __name__ == '__main__':
    main()
