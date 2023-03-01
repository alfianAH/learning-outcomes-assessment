# Generated by Django 3.2 on 2022-10-28 06:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_myuser_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fakultas',
            fields=[
                ('id_neosia', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('nama', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='myuser',
            name='fakultas',
        ),
        migrations.CreateModel(
            name='ProgramStudi',
            fields=[
                ('id_neosia', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('nama', models.CharField(max_length=100)),
                ('fakultas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.fakultas')),
            ],
        ),
        migrations.AlterField(
            model_name='myuser',
            name='prodi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.programstudi'),
        ),
    ]