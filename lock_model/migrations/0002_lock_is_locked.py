# Generated by Django 3.2 on 2023-02-17 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lock_model', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lock',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
    ]
