# Generated by Django 3.2 on 2023-02-20 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0015_matakuliahsemester_is_clo_locked'),
    ]

    operations = [
        migrations.AddField(
            model_name='matakuliahsemester',
            name='is_rps_locked',
            field=models.BooleanField(default=False),
        ),
    ]
