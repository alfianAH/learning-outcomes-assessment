# Generated by Django 3.2 on 2022-11-18 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('semester', '0002_auto_20221111_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='semester',
            name='tipe_semester',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Ganjil'), (2, 'Genap')]),
        ),
    ]