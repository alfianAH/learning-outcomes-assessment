# Generated by Django 3.2 on 2023-04-01 05:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ilo', '0007_ilo_persentase_capaian_ilo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ilo',
            name='persentase_capaian_ilo',
        ),
    ]