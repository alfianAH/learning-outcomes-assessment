# Generated by Django 3.2 on 2022-12-08 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ilo', '0003_auto_20221208_1405'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformanceIndicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deskripsi', models.TextField()),
                ('ilo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ilo.ilo')),
            ],
        ),
    ]
