# Generated by Django 3.2 on 2023-09-04 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_rename_name_myuser_nama'),
    ]

    operations = [
        migrations.AddField(
            model_name='programstudi',
            name='is_restricted_mode',
            field=models.BooleanField(default=True),
        ),
    ]
