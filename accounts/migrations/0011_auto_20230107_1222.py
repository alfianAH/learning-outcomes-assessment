# Generated by Django 3.2 on 2023-01-07 04:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_programstudi_fakultas'),
    ]

    operations = [
        migrations.CreateModel(
            name='JenjangStudi',
            fields=[
                ('id_neosia', models.BigIntegerField(primary_key=True, serialize=False, unique=True)),
                ('nama', models.CharField(max_length=255)),
                ('kode', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='fakultas',
            name='id_neosia',
            field=models.BigIntegerField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='programstudi',
            name='id_neosia',
            field=models.BigIntegerField(primary_key=True, serialize=False, unique=True),
        ),
        migrations.CreateModel(
            name='ProgramStudiJenjang',
            fields=[
                ('id_neosia', models.BigIntegerField(primary_key=True, serialize=False, unique=True)),
                ('jenjang_studi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.jenjangstudi')),
                ('program_studi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.programstudi')),
            ],
        ),
    ]
