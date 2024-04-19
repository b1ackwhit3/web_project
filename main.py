from flask import Flask, render_template, redirect, url_for
from data import db_session
from data.users import User
from data.reviews import Review
import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.login import LoginForm
from forms.reg import RegisterForm
from forms.make_review import ReviewForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    return render_template('base.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, message='Пароли разные')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, message='Пользователь уже существует')
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        f = form.photo.data
        if f:
            f.save(f'static/img/pfp/{form.name.data}.png')
            user.have_photo = True
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, remember=True)
        return redirect('/')
    return render_template('register.html', title='Регистрация',
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', title='Авторизация',
                               message='Неверный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/delete_profile')
@login_required
def delete_profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == current_user.name).first()
    os.remove(f'D:\group_web_project\static\img\pfp\{user.name}.png')
    db_sess.delete(user)
    db_sess.commit()
    return redirect('/')


@app.route('/make_review')
@login_required
def make_review():
    form = ReviewForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        review = Review(
            place_name=form.place_name.data,
            mark=form.mark.data,
            opinion=form.opinion.data,
            user_id=current_user.id
        )
        db_sess.add(review)
        db_sess.commit()
        return redirect('/')
    return render_template('make_review.html', title='Создать отзыв',
                           form=form)


@login_required
def profile():
    return render_template('profile.html')


def main():
    db_session.global_init('db/travel.db')
    app.run()


if __name__ == '__main__':
    main()