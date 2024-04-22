from flask import Flask, render_template, redirect
from data import db_session
from data.users import User
from data.reviews import Review
import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.login import LoginForm
from forms.reg import RegisterForm
from forms.make_review import ReviewForm
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    lastnews = []
    for r in db_sess.query(Review).order_by(Review.id.desc()).limit(3).all():
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        params = {
            'apikey': api_key,
            'text': r.place_name,
            'lang': 'ru_RU',
            'type': 'biz'
        }
        response = requests.get(search_api_server, params=params)
        json_response = response.json()
        organization = json_response["features"][0]
        org_name = organization["properties"]["CompanyMetaData"]["name"]
        org_address = organization["properties"]["CompanyMetaData"]["address"]
        point = organization["geometry"]["coordinates"]
        org_point = "{0},{1}".format(point[0], point[1])
        delta = "0.005"
        ll = org_point
        spn = ",".join([delta, delta])
        l = "map"
        pt = "{0},pm2dgl".format(org_point)
        map_api_server = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={l}&pt={pt}"
        lastnews.append((r.place_name, map_api_server, r.mark, r.opinion))
    return render_template('index.html', lastnews=lastnews)


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
    os.remove(os.path.abspath(f'static/img/pfp/{current_user.name}.png'))
    for r in db_sess.query(Review).filter(Review.user_id == current_user.id):
        db_sess.delete(r)
    db_sess.delete(user)
    db_sess.commit()
    logout_user()
    return redirect('/')


@app.route('/make_review', methods=['GET', 'POST'])
@login_required
def make_review():
    form = ReviewForm()
    if form.validate_on_submit():


        try:
            search_api_server = "https://search-maps.yandex.ru/v1/"
            api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
            params = {
                'apikey': api_key,
                'text': form.place_name.data,
                'lang': 'ru_RU',
                'type': 'biz'
            }
            response = requests.get(search_api_server, params=params)
        except Exception:
            return render_template('make_review.html', title='Создать отзыв',
                                   form=form, err=True)
        if not response:
            return render_template('make_review.html', title='Создать отзыв',
                                   form=form, err=True)
        try:
            json_response = response.json()
            organization = json_response["features"][0]
            org_name = organization["properties"]["CompanyMetaData"]["name"]
            org_address = organization["properties"]["CompanyMetaData"]["address"]
            point = organization["geometry"]["coordinates"]
            org_point = "{0},{1}".format(point[0], point[1])
            delta = "0.005"
            ll = org_point
            spn = ",".join([delta, delta])
            l = "map"
            pt = "{0},pm2dgl".format(org_point)
            map_api_server = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={l}&pt={pt}"
        except Exception:
            return render_template('make_review.html', title='Создать отзыв',
                                   form=form, err=True)


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


@login_required
@app.route('/check_review')
def check_review():
    db_sess = db_session.create_session()
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    files = []
    for r in db_sess.query(Review).filter(Review.user_id == current_user.id):
        params = {
            'apikey': api_key,
            'text': r.place_name,
            'lang': 'ru_RU',
            'type': 'biz'
        }
        response = requests.get(search_api_server, params=params)
        json_response = response.json()
        organization = json_response["features"][0]
        org_name = organization["properties"]["CompanyMetaData"]["name"]
        org_address = organization["properties"]["CompanyMetaData"]["address"]
        point = organization["geometry"]["coordinates"]
        org_point = "{0},{1}".format(point[0], point[1])
        delta = "0.005"
        ll = org_point
        spn = ",".join([delta, delta])
        l = "map"
        pt = "{0},pm2dgl".format(org_point)
        map_api_server = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={l}&pt={pt}"
        files.append((r.place_name, map_api_server, r.mark, r.opinion))
    return render_template('check_review.html', files=files)


@app.route('/review/<string:place_name>')
def review(place_name):
    db_sess = db_session.create_session()
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    params = {
        'apikey': api_key,
        'text': place_name,
        'lang': 'ru_RU',
        'type': 'biz'
    }
    response = requests.get(search_api_server, params=params)
    json_response = response.json()
    organization = json_response["features"][0]
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    delta = "0.005"
    ll = org_point
    spn = ",".join([delta, delta])
    l = "map"
    pt = "{0},pm2dgl".format(org_point)
    map_api_server = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={l}&pt={pt}"
    n = db_sess.query(Review).filter(Review.place_name == place_name).count()
    summa = 0
    for el in db_sess.query(Review).filter(Review.place_name == place_name).all():
        summa += el.mark
    sr = 0
    try:
        sr = summa/n
    except Exception:
        pass
    return render_template('review.html', place_name=place_name, p=map_api_server, sr=sr)



def main():
    db_session.global_init('db/travel.db')
    app.run()


if __name__ == '__main__':
    main()