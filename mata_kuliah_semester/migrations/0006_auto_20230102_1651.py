# Generated by Django 3.2 on 2023-01-02 08:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_kurikulum', '0001_initial'),
        ('mata_kuliah_semester', '0005_auto_20230102_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matakuliahsemester',
            name='mk_kurikulum',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah_kurikulum.matakuliahkurikulum'),
        ),
        migrations.DeleteModel(
            name='MataKuliahKurikulum',
        ),
    ]
