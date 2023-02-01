# Generated by Django 3.2 on 2023-01-24 08:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0013_auto_20230119_2101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nilaimatakuliahmahasiswa',
            name='peserta',
        ),
        migrations.AddField(
            model_name='pesertamatakuliah',
            name='nilai_akhir',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
        migrations.AddField(
            model_name='pesertamatakuliah',
            name='nilai_huruf',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AddConstraint(
            model_name='pesertamatakuliah',
            constraint=models.CheckConstraint(check=models.Q(('nilai_akhir__gte', 0.0), ('nilai_akhir__lte', 100.0)), name='nilai_akhir_range'),
        ),
        migrations.DeleteModel(
            name='NilaiMataKuliahMahasiswa',
        ),
    ]