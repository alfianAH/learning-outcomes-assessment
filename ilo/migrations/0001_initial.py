# Generated by Django 3.2 on 2022-12-05 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ilo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('deskripsi', models.TextField()),
                ('satisfactory_level', models.FloatField()),
                ('persentase_capaian_ilo', models.FloatField(null=True)),
            ],
        ),
    ]
