from flask import Flask, render_template, redirect, request, make_response, session
from data import db_session
import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365)


@app.route('/')
def index():
    return render_template('base.html', log_in=True, username='Вася Петров')

"""
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
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация',
                           form=form)


@app.route('/cookie')
def cookie_test():
    visits_count = int(request.cookies.get('visits_count', 0))
    if visits_count:
        ans = make_response(f'Вы пришли на страницу {visits_count + 1} раз')
        ans.set_cookie('visits_count', str(visits_count + 1), max_age=60 * 60 * 24)
    else:
        ans = make_response(f'Вы пришли на страницу первый раз за сутки')
        ans.set_cookie('visits_count', '1', max_age=60 * 60 * 24)
    return ans


@app.route('/session')
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(f'Вы пришли на страницу {visits_count + 1} раз')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
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

"""


def main():
    db_session.global_init('db/travel.db')
    app.run()


if __name__ == '__main__':
    main()