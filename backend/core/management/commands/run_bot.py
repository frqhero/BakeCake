import logging
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.ext import Updater
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def main():
    tg_bot_token = settings.TG_BOT_TOKEN
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
