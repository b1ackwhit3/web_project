import logging
from email_validate import validate
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from data import db_session
from data.users import User

log_in = False
curr_user_id = None
l = lambda x: 'a' <= x <= 'я' or 'А' <= x <= 'Я' or '0' <= x <= '9' or x in (' ', '_')
temail, tname, tpassword = None, None, None
wait_name = None
BOT_TOKEN = '7003047434:AAFLOJSvtnsxSb2eosLtMxKa3xzKY002uME'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.ERROR
)
logger = logging.getLogger(__name__)
db_session.global_init("db/travel.db")

back_keyboard = ReplyKeyboardMarkup([['/no']], one_time_keyboard=True, resize_keyboard=True)
markup = ReplyKeyboardMarkup([['/reg'], ['/login']], one_time_keyboard=True, resize_keyboard=True)


async def start(update, context):
    await update.message.reply_text('Привет. Тут будет приветствие получше.', reply_markup=markup)


async def reg(update, context):
    temp_keyboard = ReplyKeyboardMarkup([['Да', '/no']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Вы хотите зарегестрироваться?', reply_markup=temp_keyboard)
    return 'add_new_email'


async def add_new_email(update, context):
    if update.message.text == 'нет':
        await update.message.reply_text('Возвращаемся...')
        return ConversationHandler.END
    await update.message.reply_text('Введите свой e-mail', reply_markup=back_keyboard)
    return 'add_new_name'


async def add_new_name(update, context):
    if not validate(update.message.text, check_smtp=False):
        await update.message.reply_text(
            'Ошибка. E-mail неправильно введён либо недоступен Попробуйте другой.',
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
    await update.message.reply_text('Как мне вас называть?', reply_markup=back_keyboard)
    return 'add_new_password'


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
    await update.message.reply_text('Спасибо за регестрацию!', reply_markup=markup)

    global tname, tpassword, temail
    tpassword = update.message.text
    user = User()
    user.name = tname
    user.email = temail
    user.password = tpassword
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()

    temail, tname, tpassword = None, None, None
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
            markup = ReplyKeyboardMarkup([['/reg'], ['/login'], ['/logout']],
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
    markup = ReplyKeyboardMarkup([['/reg'], ['/login']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Вы вышли из своего аккаунта', reply_markup=markup)
    curr_user_id, log_in = None, False


async def no(update, context):
    await update.message.reply_text("Возращаемся...", reply_markup=markup)
    global tname, tpassword, temail
    temail, tname, tpassword = None, None, None
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('logout', logout))

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
