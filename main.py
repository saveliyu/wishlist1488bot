# Импортируем необходимые классы.
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from config import BOT_TOKEN

import telegram
from db_dispatcher import add_user, add_wishlist, take_wihslists

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update, context):
    add_user(update.message.chat.username)
    reply_keyboard = [['Мои вишлисты', 'Найти вишлист']]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
        'Привет! Я - бот, с помощью которого ты можешь создать список своих желаний и поделиться им с друзьями!' +
        '\n\nЧто бы начать, нажми "Мои вишлисты", а затем "Cоздать новый"\n' +
        'Если тебя сюда пригласил друг, то нажимай "Найти вишлист"',
        reply_markup=markup
    )
    return 'first_response'


async def first_response(update, context):
    if update.message.text == 'Мои вишлисты':
        reply_keyboard = [['Создать новый', 'Выбрать из существующих']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
        count_of_lists = len(take_wihslists(update.message.chat.username))
        await update.message.reply_text(f"У вас есть {count_of_lists} вишлистов, хотите выбрать какой-то из существующих или создать " +
                                        "новый?", reply_markup=markup)
        return 'my_wishlists'
    elif update.message.text == 'Найти вишлист':
        await update.message.reply_text("Введите код, который вам сказал ваш друг", reply_markup=ReplyKeyboardRemove())
        return 'search_wishlist'
    else:
        reply_keyboard = [['Мои вишлисты', 'Найти вишлист']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("Я вас не понимаю! Используйте уже готовые кнопки с командами.",
                                        reply_markup=markup)
        return 'first_response'


async def my_wishlists(update, context):
    if update.message.text == 'Создать новый':
        await update.message.reply_text("Для начала введите название вашего вишлиста", reply_markup=ReplyKeyboardRemove())
        return 'named_wishlist'
    elif update.message.text == 'Выбрать из существующих':
        lists = take_wihslists(update.message.chat.username)
        text = "Вот ваши созданные списки желаний:\n"
        for num, list in enumerate(lists):
            text += str(num + 1) + " *" + list[-1] + '*\n'
        await update.message.reply_text(text + "Введите порядковый номер вишлиста который хотите посмотреть",
                                        reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
        return 'chose_my_wishlist'
    else:
        reply_keyboard = [['Создать новый', 'Выбрать из существующих']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text("Я вас не понимаю! Используйте уже готовые кнопки с командами.",
                                        reply_markup=markup)
        return 'my_wishlists'


async def search_wishlist(update, context):
    pass


async def named_wishlist(update, context):
    if update.message.text:
        code = add_wishlist(update.message.chat.username, update.message.text)

        reply_keyboard = [['Добавить хотелку', 'Удалить вишлист']]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
        await update.message.reply_text(f"Отлично ваш вишлист {update.message.text} создан!\n" +
                                        f"Его ункальный код: {code}",
                                        reply_markup=markup)

        return 'created_wishlist'
    else:
        await update.message.reply_text("Пожалуйста, введите название используюя только текст и не присылая " +
                                        "сторонние файлы",
                                        reply_markup=ReplyKeyboardRemove())
        return 'named_wishlist'


async def created_wishlist(update, context):
    if update.message.text == 'Добавить хотелку':
        await update.message.reply_text("Как называется вещь которую вы хотите добавить?",
                                        reply_markup=ReplyKeyboardRemove())
        return 'named_item'
    elif update.message.text == 'Удалить вишлист':
        await update.message.reply_text("Введите порядковый номер вишлиста который хотите посмотреть",
                                        reply_markup=ReplyKeyboardRemove())
        return 'chose_my_wishlist'
    else:
        await update.message.reply_text("Я вас не понимаю! Используйте уже готовые кнопки с командами.",
                                        reply_markup=ReplyKeyboardRemove())
        return 'created_wishlist'



async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            'first_response': [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            'my_wishlists': [MessageHandler(filters.TEXT & ~filters.COMMAND, my_wishlists)],
            'search_wishlist': [MessageHandler(filters.TEXT & ~filters.COMMAND, search_wishlist)],
            'named_wishlist': [MessageHandler(filters.TEXT & ~filters.COMMAND, named_wishlist)],
            'created_wishlist': [MessageHandler(filters.TEXT & ~filters.COMMAND, created_wishlist)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()