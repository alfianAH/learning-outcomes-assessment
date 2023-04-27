import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Deletes laporan CPL images older than a certain period'

    def handle(self, *args, **options):
        now = datetime.now()
        laporan_cpl_dir = os.path.join(settings.STATIC_ROOT, 'laporan_cpl', 'charts')

        for filename in os.listdir(laporan_cpl_dir):
            filepath = os.path.join(laporan_cpl_dir, filename)
            
            # If not a file, skip
            if not os.path.isfile(filepath): continue

            filetime = datetime.fromtimestamp(os.path.getctime(filepath))
            age = now - filetime

            # If file's age is older or equal than 1 day, remove file 
            if age.days >= 1: os.remove(filepath)
