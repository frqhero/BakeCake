import os

from django.core.management.base import BaseCommand
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup_management.settings')
django.setup()


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
