import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler

BOT_TOKEN='7003047434:AAFLOJSvtnsxSb2eosLtMxKa3xzKY002uME'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text('Привет. Тут будет приветствие получше.')


async def helper(update, context):
    await update.message.reply_text('Тут будет помощь')


async def answerer(update, context):
    await update.message.reply_text('Не пиши сюда')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', helper))
    application.add_handler(MessageHandler(filters.TEXT, answerer))
    application.run_polling()


if __name__ == '__main__':
    main()