# Generated by Django 3.2 on 2023-01-27 08:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pi_area', '0005_auto_20221230_1803'),
        ('mata_kuliah_semester', '0014_auto_20230124_1610'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('deskripsi', models.TextField()),
                ('mk_semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah_semester.matakuliahsemester')),
            ],
        ),
        migrations.CreateModel(
            name='KomponenClo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teknik_penilaian', models.CharField(max_length=255)),
                ('instrumen_penilaian', models.CharField(max_length=255)),
                ('persentase', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('clo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clo.clo')),
            ],
        ),
        migrations.CreateModel(
            name='PiClo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clo.clo')),
                ('performance_indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pi_area.performanceindicator')),
            ],
        ),
        migrations.CreateModel(
            name='NilaiKomponenCloPeserta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nilai', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('komponen_clo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clo.komponenclo')),
                ('peserta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah_semester.pesertamatakuliah')),
            ],
        ),
        migrations.AddConstraint(
            model_name='nilaikomponenclopeserta',
            constraint=models.CheckConstraint(check=models.Q(('nilai__gte', 0.0), ('nilai__lte', 100.0)), name='nilai_range'),
        ),
        migrations.AddConstraint(
            model_name='komponenclo',
            constraint=models.CheckConstraint(check=models.Q(('persentase__gte', 0.0), ('persentase__lte', 100.0)), name='persentase_range'),
        ),
    ]
