import logging
from email_validate import validate
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
import telegram
from data import db_session
from data.users import User
from data.reviews import Review
import requests
import aiohttp

log_in = False
curr_user_id = None
l = lambda x: 'a' <= x <= 'я' or 'А' <= x <= 'Я' or '0' <= x <= '9' or x in (' ', '_')
temail, tname, tpassword = None, None, None
torg, tmark, topinion = None, None, None
wait_name = None
BOT_TOKEN = '7003047434:AAF6gtRtvsz2ybhNV3TEfFDdVzF4r45YfGE'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR
)
logger = logging.getLogger(__name__)
db_session.global_init("db/travel.db")

back_keyboard = ReplyKeyboardMarkup([['/no']], one_time_keyboard=True,
                                    resize_keyboard=True)
markup = ReplyKeyboardMarkup([['/reg'], ['/login']], one_time_keyboard=True,
                             resize_keyboard=True)
onetofive = ReplyKeyboardMarkup([['1'], ['2'], ['3'], ['4'], ['5'], ['/no']],
                                one_time_keyboard=True, resize_keyboard=True)
temp_keyboard = ReplyKeyboardMarkup([['Да', '/no']], one_time_keyboard=True,
                                        resize_keyboard=True)

async def start(update, context):
    await update.message.reply_text('Привет, это бот Traveler! Тут ты можешь оставлять отзывы на' +
                                    f' места\n\nВот список команд:\n/reg - Зарегестрироваться\n/' +
                                    f'login - Войти', reply_markup=markup)
    await context.bot.send_photo(
        update.message.chat_id,
        open('static/img/main_jpg.png', 'rb')
    )


async def reg(update, context):
    await update.message.reply_text('Вы хотите зарегестрироваться?\n\n/no - вернуться',
                                    reply_markup=temp_keyboard)
    return 'add_new_email'


async def add_new_email(update, context):
    await update.message.reply_text('Введите свой e-mail', reply_markup=back_keyboard)
    return 'add_new_name'


async def add_new_name(update, context):
    try:
        if not validate(update.message.text, check_smtp=False):
            await update.message.reply_text(
                'Ошибка. E-mail неправильно введён либо недоступен ',
                'Попробуйте другой.',
                reply_markup=back_keyboard)
            return 'add_new_name'
        db_sess = db_session.create_session()
        for user in db_sess.query(User).all():
            if update.message.text == user.email:
                await update.message.reply_text('Пользователь с такой почтой уже есть!',
                                                reply_markup=back_keyboard)
                return 'add_new_name'
        global temail
        temail = update.message.text
        await update.message.reply_text('Как мне вас называть?',
                                        reply_markup=back_keyboard)
        return 'add_new_password'
    except telegram.error.BadRequest:
        await update.message.reply_text(
            'Ошибка. E-mail неправильно введён либо недоступен ',
            'Попробуйте другой.',
            reply_markup=back_keyboard)
        return 'add_new_name'
    except Exception:
        await update.message.reply_text(
            'Ошибка. E-mail неправильно введён либо недоступен ',
            'Попробуйте другой.',
            reply_markup=back_keyboard)
        return 'add_new_name'


async def add_new_password(update, context):
    if len(update.message.text) < 3:
        await update.message.reply_text('Имя слишком короткое!', reply_markup=back_keyboard)
        return 'add_new_password'
    if len(update.message.text) > 22:
        await update.message.reply_text('Имя слишком длинное!', reply_markup=back_keyboard)
        return 'add_new_password'
    try:
        global l
        if not all(l(el) for el in list(update.message.text)):
            await update.message.reply_text(' '.join(['В имени должны быть только',
                                                      'буквы русской раскладки в любом регистре,',
                                                      'цифры, пробелы и символ "_"']),
                                            reply_markup=back_keyboard)
            return 'add_new_password'
    except Exception as e:
        await update.message.reply_text(' '.join(['В имени должны быть только',
                                                  'буквы русской раскладки в любом регистре,',
                                                  'цифры, пробелы и символ "_"']),
                                        reply_markup=back_keyboard)
        return 'add_new_password'

    db_sess = db_session.create_session()
    for user in db_sess.query(User).all():
        if update.message.text == user.name:
            await update.message.reply_text('Пользователь с таким именем уже есть!',
                                            reply_markup=back_keyboard)
            return 'add_new_password'
    global tname
    tname = update.message.text
    await update.message.reply_text('Введите пароль', reply_markup=back_keyboard)
    return 'end_reg'


async def end_reg(update, context):
    if len(update.message.text) < 3:
        await update.message.reply_text('Пароль слишком короткий!', reply_markup=back_keyboard)
        return 'end_reg'
    if len(update.message.text) > 22:
        await update.message.reply_text('Пароль слишком длинный!', reply_markup=back_keyboard)
        return 'end_reg'

    global tname, tpassword, temail
    tpassword = update.message.text
    user = User()
    user.name = tname
    user.email = temail
    user.password = tpassword
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()

    global markup
    markup = ReplyKeyboardMarkup([['/reg'], ['/login'], ['/logout'], ['/make_review'],
                                  ['/see_reviews']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Спасибо за регестрацию!', reply_markup=markup)

    global log_in, curr_user_id
    log_in = True
    for u in db_sess.query(User).filter(User.name == user.name):
        curr_user_id = u.id

    return ConversationHandler.END


async def login(update, context):
    await update.message.reply_text('Введите ваше имя', reply_markup=back_keyboard)
    return 'entry_name'


async def entry_name(update, context):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).all():
        if user.name == update.message.text:
            await update.message.reply_text('Введите пароль', reply_markup=back_keyboard)
            global wait_name
            wait_name = update.message.text
            return 'entry_password'
    await update.message.reply_text('Пользователь с таким именем не найден',
                                    reply_markup=back_keyboard)
    return 'entry_name'


async def entry_password(update, context):
    db_sess = db_session.create_session()
    global wait_name, markup
    for user in db_sess.query(User).filter(User.name == wait_name):
        if user.password == update.message.text:
            markup = ReplyKeyboardMarkup([['/reg'], ['/login'], ['/logout'],
                                          ['/make_review'], ['/see_reviews']],
                                         one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text('Вы успешно вошли!', reply_markup=markup)
            global log_in, curr_user_id
            log_in = True
            curr_user_id = user.id
            return ConversationHandler.END
    await update.message.reply_text('Неверный пароль', reply_markup=back_keyboard)
    return 'entry_password'


async def logout(update, context):
    global curr_user_id, log_in, markup
    if not log_in:
        await update.message.reply_text('Вы еще не вошли', reply_markup=markup)
        return
    markup = ReplyKeyboardMarkup([['/reg'], ['/login']], one_time_keyboard=True,
                                 resize_keyboard=True)
    await update.message.reply_text('Вы вышли из своего аккаунта', reply_markup=markup)
    curr_user_id, log_in = None, False


async def make_review(update, context):
    if not log_in:
        await update.message.reply_text('Анонимные отзывы оставлять нельзя!\n\n/no - вернуться', reply_markup=markup)
        return
    await update.message.reply_text('Выберите место', reply_markup=back_keyboard)
    return 'which_place'


async def which_place(update, context):
    try:
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
        params = {
            'apikey': api_key,
            'text': update.message.text,
            'lang': 'ru_RU',
            'type': 'biz'
        }
        response = requests.get(search_api_server, params=params)
    except Exception:
        await update.message.reply_text('Такое место не найдено', reply_markup=back_keyboard)
        return 'which_place'
    if not response:
        await update.message.reply_text('Такое место не найдено', reply_markup=back_keyboard)
        return 'which_place'
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
        await update.message.reply_text('Такое место не найдено', reply_markup=back_keyboard)
        return 'which_place'
    await context.bot.send_photo(
        update.message.chat_id,
        map_api_server,
        caption="Нашёл:"
    )
    global torg
    torg = org_name + ', ' + org_address
    await update.message.reply_text('Оцените это место от 1 до 5', reply_markup=onetofive)
    return 'mark_it'


async def mark_it(update, context):
    try:
        if int(update.message.text) not in range(1, 6):
            await update.message.reply_text('Вы ввели не число из диапозона от 1 до 5',
                                            reply_markup=onetofive)
            return 'mark_it'
    except Exception:
        await update.message.reply_text('Вы ввели не число из диапозона от 1 до 5',
                                        reply_markup=onetofive)
        return 'mark_it'
    global tmark
    tmark = int(update.message.text)
    await update.message.reply_text('Скажите пару слов об этом месте', reply_markup=back_keyboard)
    return 'opinion'


async def opinion(update, context):
    if len(update.message.text) < 6:
        await update.message.reply_text('Слишком короткий отзыв!', reply_markup=back_keyboard)
        return 'opinion'
    if len(update.message.text) > 100:
        await update.message.reply_text('Слишком длинный отзыв!', reply_markup=back_keyboard)
        return 'opinion'
    global torg, tmark, topinion
    topinion = update.message.text

    r = Review()
    r.place_name = torg
    r.mark = tmark
    r.opinion = topinion
    r.user_id = curr_user_id
    db_sess = db_session.create_session()
    db_sess.add(r)
    db_sess.commit()

    await update.message.reply_text('Спасибо за отзыв!', reply_markup=markup)

    return ConversationHandler.END


async def no(update, context):
    await update.message.reply_text("Возращаемся...", reply_markup=markup)
    return ConversationHandler.END


async def see_reviews(update, context):
    if not log_in:
        await update.message.reply_text('Я не знаю твои отзывы!' +
                                        'Представься, аноним!\n\n/no - вернуться',
                                        reply_markup=markup)
        return
    db_sess = db_session.create_session()
    if len(list(db_sess.query(Review).filter(Review.user_id == curr_user_id))) == 0:
        await update.message.reply_text('У тебя нет отзывов! Сделай их!' +
                                        '\n\n/no - вернуться',
                                        reply_markup=markup)
        return
    for r in db_sess.query(Review).filter(Review.user_id == curr_user_id):
        await update.message.reply_text(f'{r.place_name} - {r.mark}/5 - {r.opinion}')
    await update.message.reply_text('Вот все твои отзывы!', reply_markup=markup)
    return


async def get_response(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('logout', logout))
    application.add_handler(CommandHandler('see_reviews', see_reviews))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('make_review', make_review)],
        states={
            'which_place': [MessageHandler(filters.TEXT & ~filters.COMMAND, which_place)],
            'mark_it': [MessageHandler(filters.TEXT & ~filters.COMMAND, mark_it)],
            'opinion': [MessageHandler(filters.TEXT & ~filters.COMMAND, opinion)]
        },
        fallbacks=[CommandHandler('no', no)]
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('reg', reg)],
        states={
            'add_new_email': [MessageHandler(filters.TEXT & ~filters.COMMAND, add_new_email)],
            'add_new_name': [MessageHandler(filters.TEXT & ~filters.COMMAND, add_new_name)],
            'add_new_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, add_new_password)],
            'end_reg': [MessageHandler(filters.TEXT & ~filters.COMMAND, end_reg)]
        },
        fallbacks=[CommandHandler('no', no)]
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            'entry_name': [MessageHandler(filters.TEXT & ~filters.COMMAND, entry_name)],
            'entry_password': [MessageHandler(filters.TEXT & ~filters.COMMAND, entry_password)]
        },
        fallbacks=[CommandHandler('no', no)]
    ))

    application.run_polling()


if __name__ == '__main__':
    main()
