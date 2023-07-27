import logging
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import Updater, CallbackContext
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def start(update: Update, context: CallbackContext) -> str:
    pass


def main():
    tg_bot_token = settings.TG_BOT_TOKEN
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    # top level conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
