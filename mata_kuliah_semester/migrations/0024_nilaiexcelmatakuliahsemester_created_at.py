# Generated by Django 3.2 on 2023-03-09 14:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0023_nilaiexcelmatakuliahsemester'),
    ]

    operations = [
        migrations.AddField(
            model_name='nilaiexcelmatakuliahsemester',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
