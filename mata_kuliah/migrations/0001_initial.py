# Generated by Django 3.2 on 2022-11-30 06:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('kurikulum', '0005_delete_matakuliahkurikulum'),
        ('accounts', '0008_remove_myuser_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='MataKuliahKurikulum',
            fields=[
                ('id_neosia', models.BigIntegerField(primary_key=True, serialize=False, unique=True)),
                ('kode', models.CharField(max_length=100)),
                ('nama', models.CharField(max_length=255)),
                ('sks', models.PositiveSmallIntegerField()),
                ('kurikulum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kurikulum.kurikulum')),
                ('prodi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.programstudi')),
            ],
        ),
    ]
