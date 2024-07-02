import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Fill tables"
    
    def handle(self, *args, **options):
        print("Fill tables")
        print(os.listdir('./core'))