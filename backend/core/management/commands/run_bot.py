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
    InlineQueryHandler,
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
        # [
        #     InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
        #     InlineKeyboardButton(text='Done', callback_data=str(END)),
        # ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if context.user_data.get('START_OVER'):
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
        )
    else:
        update.message.reply_text('Добро пожаловать в Bake Cake! 🎂🎂🎂')
        image_response = requests.get(
            'https://www.ilovecake.ru/data/images/designer-cake.png'
        )
        update.message.reply_photo(image_response.content)
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data['START_OVER'] = False
    return 'SELECT_CAKE_TYPE'


def get_complete_cakes(update: Update, context: CallbackContext) -> str:
    # send a message and then return select_cake_type
    pass


def create_custom_cake(update: Update, context: CallbackContext) -> str:
    # send a message and then return select_cake_type
    pass


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')

    return 'END'


def main():
    tg_bot_token = settings.TG_BOT_TOKEN
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    # top level conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            'SELECT_CAKE_TYPE': [
                InlineQueryHandler(get_complete_cakes),
                InlineQueryHandler(create_custom_cake),
            ]
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
