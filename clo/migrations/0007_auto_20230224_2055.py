# Generated by Django 3.2 on 2023-02-24 12:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clo', '0006_auto_20230222_1644'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clo',
            options={'ordering': ['nama']},
        ),
        migrations.AlterModelOptions(
            name='nilaiclomatakuliahsemester',
            options={'ordering': ['clo__nama']},
        ),
    ]