# Generated by Django 3.2 on 2023-03-29 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_kurikulum', '0004_remove_matakuliahkurikulum_prodi_jenjang'),
    ]

    operations = [
        migrations.AddField(
            model_name='matakuliahkurikulum',
            name='praktek_sks',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='matakuliahkurikulum',
            name='teori_sks',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
