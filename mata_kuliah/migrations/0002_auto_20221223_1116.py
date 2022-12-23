# Generated by Django 3.2 on 2022-12-23 03:16

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('semester', '0004_alter_tahunajaran_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ilo', '0005_auto_20221223_1116'),
        ('mata_kuliah', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MataKuliahSemester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('average_clo_achievement', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('mk_kurikulum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah.matakuliahkurikulum')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='semester.semesterkurikulum')),
            ],
        ),
        migrations.CreateModel(
            name='PesertaMataKuliah',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kelas', models.CharField(max_length=20)),
                ('mahasiswa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('mk_semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah.matakuliahsemester')),
            ],
        ),
        migrations.CreateModel(
            name='NilaiMataKuliahMahasiswa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nilai_akhir', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('peserta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah.pesertamatakuliah')),
            ],
        ),
        migrations.CreateModel(
            name='NilaiMataKuliahIloMahasiswa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nilai_ilo', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('ilo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ilo.ilo')),
                ('peserta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah.pesertamatakuliah')),
            ],
        ),
        migrations.CreateModel(
            name='DosenMataKuliah',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mahasiswa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('mk_semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah.matakuliahsemester')),
            ],
        ),
        migrations.AddConstraint(
            model_name='nilaimatakuliahmahasiswa',
            constraint=models.CheckConstraint(check=models.Q(('nilai_akhir__gte', 0.0), ('nilai_akhir__lte', 100.0)), name='nilai_akhir_range'),
        ),
        migrations.AddConstraint(
            model_name='nilaimatakuliahilomahasiswa',
            constraint=models.CheckConstraint(check=models.Q(('nilai_ilo__gte', 0.0), ('nilai_ilo__lte', 100.0)), name='nilai_ilo_range'),
        ),
        migrations.AddConstraint(
            model_name='matakuliahsemester',
            constraint=models.CheckConstraint(check=models.Q(('average_clo_achievement__gte', 0.0), ('average_clo_achievement__lte', 100.0)), name='average_clo_achievement_range'),
        ),
    ]
