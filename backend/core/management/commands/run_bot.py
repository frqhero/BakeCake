import os

from django.core.management.base import BaseCommand
from django.conf import settings
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup_management.settings')
django.setup()


def main():
    tg_bot_token = settings.TG_BOT_TOKEN


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
