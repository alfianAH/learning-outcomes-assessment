# Generated by Django 3.2 on 2023-03-01 14:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0019_pesertamatakuliah_status_nilai'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesertamatakuliah',
            name='average_clo_achievement',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)]),
        ),
        migrations.AddConstraint(
            model_name='pesertamatakuliah',
            constraint=models.CheckConstraint(check=models.Q(('average_clo_achievement__gte', 0.0), ('average_clo_achievement__lte', 100.0)), name='average_clo_achievement_peserta_range'),
        ),
    ]
