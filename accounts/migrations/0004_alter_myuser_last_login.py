# Generated by Django 3.2 on 2022-10-25 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_myuser_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]