import logging
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, ConversationHandler, InlineQueryHandler
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def start(update: Update, context: CallbackContext) -> str:
    # send a message and then return select_cake_type
    pass

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
            'SELECT_CAKE_TYPE': [InlineQueryHandler(get_complete_cakes), InlineQueryHandler(create_custom_cake)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
