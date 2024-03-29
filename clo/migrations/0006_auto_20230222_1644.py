# Generated by Django 3.2 on 2023-02-22 08:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0017_auto_20230222_1644'),
        ('clo', '0005_piclo_lock'),
    ]

    operations = [
        migrations.CreateModel(
            name='NilaiCloMataKuliahSemester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nilai', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='nilaikomponenclopeserta',
            name='nilai_range',
        ),
        migrations.AddConstraint(
            model_name='nilaikomponenclopeserta',
            constraint=models.CheckConstraint(check=models.Q(('nilai__gte', 0.0), ('nilai__lte', 100.0)), name='nilai_komponen_clo_range'),
        ),
        migrations.AddField(
            model_name='nilaiclomatakuliahsemester',
            name='clo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clo.clo'),
        ),
        migrations.AddField(
            model_name='nilaiclomatakuliahsemester',
            name='mk_semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah_semester.matakuliahsemester'),
        ),
        migrations.AddConstraint(
            model_name='nilaiclomatakuliahsemester',
            constraint=models.CheckConstraint(check=models.Q(('nilai__gte', 0.0), ('nilai__lte', 100.0)), name='nilai_clo_mk_semester_range'),
        ),
    ]
