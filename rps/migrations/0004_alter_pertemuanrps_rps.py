# Generated by Django 3.2 on 2023-03-29 09:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0024_nilaiexcelmatakuliahsemester_created_at'),
        ('rps', '0003_alter_rencanapembelajaransemester_mk_semester'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pertemuanrps',
            name='rps',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah_semester.matakuliahsemester'),
        ),
    ]
