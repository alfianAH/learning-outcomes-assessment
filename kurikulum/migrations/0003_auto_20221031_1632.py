# Generated by Django 3.2 on 2022-10-31 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kurikulum', '0002_auto_20221031_1550'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kurikulum',
            name='id',
        ),
        migrations.AddField(
            model_name='kurikulum',
            name='id_neosia',
            field=models.BigIntegerField(default=1, primary_key=True, serialize=False, unique=True),
            preserve_default=False,
        ),
    ]
