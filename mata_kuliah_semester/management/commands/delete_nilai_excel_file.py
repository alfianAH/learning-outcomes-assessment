import os
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from mata_kuliah_semester.models import NilaiExcelMataKuliahSemester


class Command(BaseCommand):
    help = 'Deletes objects older than a certain period'

    def handle(self, *args, **options):
        period = timedelta(days=1)
        older_than = timezone.now() - period
        nilai_qs = NilaiExcelMataKuliahSemester.objects.filter(
            created_at__lt=older_than)
        
        # Remove file from disk
        for nilai_obj in nilai_qs:
            os.remove(nilai_obj.file.path)

        nilai_qs.delete()
