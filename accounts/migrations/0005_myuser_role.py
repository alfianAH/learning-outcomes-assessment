# Generated by Django 3.2 on 2022-10-26 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_myuser_last_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='role',
            field=models.CharField(choices=[('a', 'Admin Program Studi'), ('d', 'Dosen'), ('m', 'Mahasiswa')], default='m', max_length=1),
            preserve_default=False,
        ),
    ]