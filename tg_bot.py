import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from data import db_session
from data.users import User

BOT_TOKEN='7003047434:AAFLOJSvtnsxSb2eosLtMxKa3xzKY002uME'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
db_session.global_init("db/travel.db")


async def start(update, context):
    await update.message.reply_text('Привет. Тут будет приветствие получше.')


async def helper(update, context):
    await update.message.reply_text('Тут будет помощь')


async def answerer(update, context):
    await update.message.reply_text('Не пиши сюда')


async def login(update, context):
    await update.message.reply_text('Введите свой логин и пароль через пробел')
    db_sess = db_session.create_session()


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', helper))
    application.add_handler(CommandHandler('login', login))
    application.run_polling()


if __name__ == '__main__':
    main()