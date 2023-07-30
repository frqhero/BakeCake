from textwrap import dedent
import logging
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def start(update: Update, context: CallbackContext) -> str:
    # send a message and then return select_cake_type
    text = dedent(
        """\
        Закажите торт!🍰 В нашем магазине вы можете
        выбрать готовый торт или собрать свой!
        Для завершения нажмите "Отменить" или наберите /stop
        """
    )

    buttons = [
        [
            InlineKeyboardButton(
                text='Готовый', callback_data=str('COMPLETED_CAKE')
            ),
            InlineKeyboardButton(
                text='Соберите свой', callback_data=str('CUSTOM_CAKE')
            ),
        ],
        [
            InlineKeyboardButton(
                text='Отменить', callback_data=str('-1')
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if context.user_data.get('START_OVER'):
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
        )
    else:
        image_response = requests.get(
            'https://www.ilovecake.ru/data/images/designer-cake.png'
        )
        update.message.reply_text('Добро пожаловать в Bake Cake! 🎂🎂🎂')
        update.message.reply_photo(image_response.content)
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data['START_OVER'] = False
    return 'SELECT_CAKE_TYPE'


def show_complete_cakes(update: Update, context: CallbackContext) -> str:
    # send a message and then return select_cake_type
    # update.callback_query.copy_message(chat_id=update.effective_chat.id)
    # update.callback_query.answer(text='')
    update.callback_query.message.reply_text('раз тортик')
    update.callback_query.message.reply_text('два тортик')
    update.callback_query.message.reply_text('три тортик')
    buttons = [
        [
            InlineKeyboardButton(
                text='Первый', callback_data=str('COMPLETED_CAKE')
            ),
            InlineKeyboardButton(
                text='Второй', callback_data=str('CUSTOM_CAKE')
            ),
            InlineKeyboardButton(
                text='Третий', callback_data=str('CUSTOM_CAKE')
            ),
            InlineKeyboardButton(
                text='Четвертый', callback_data=str('CUSTOM_CAKE')
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text('выберите тортик', reply_markup=keyboard)

    return 'SHOWING_COMPLETED_CAKES'


def create_custom_cake(update: Update, context: CallbackContext) -> str:
    # send a message and then return select_cake_type
    pass


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text('Удаляем беседу тогда...')

    return -1


def end(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer('Удаляем беседу тогда...')
    update.callback_query.delete_message()

    return -1


def main():
    tg_bot_token = settings.TG_BOT_TOKEN
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    # completed_cakes_conv_handler = ConversationHandler(
    #     entry_points=[],
    #     states=[],
    #     fallbacks=[]
    # )

    # top level conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            'SELECT_CAKE_TYPE': [
                CallbackQueryHandler(show_complete_cakes, pattern='^COMPLETED_CAKE$'),
                CallbackQueryHandler(create_custom_cake, pattern='^CUSTOM_CAKE$'),
                CallbackQueryHandler(end, pattern='^-1$'),
            ],
            # 'SHOWING_COMPLETED_CAKES': [completed_cakes_conv_handler],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
