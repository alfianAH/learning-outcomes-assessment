# Generated by Django 3.2 on 2022-12-08 06:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pi_area', '0001_initial'),
        ('ilo', '0002_ilo_semester'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ilo',
            name='semester',
        ),
        migrations.AddField(
            model_name='ilo',
            name='pi_area',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='pi_area.performanceindicatorarea'),
            preserve_default=False,
        ),
    ]
