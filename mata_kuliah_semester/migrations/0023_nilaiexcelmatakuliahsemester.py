# Generated by Django 3.2 on 2023-03-08 06:31

from django.db import migrations, models
import django.db.models.deletion
import learning_outcomes_assessment.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0022_auto_20230302_2115'),
    ]

    operations = [
        migrations.CreateModel(
            name='NilaiExcelMataKuliahSemester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(null=True, upload_to=learning_outcomes_assessment.utils.nilai_excel_upload_handler)),
                ('mk_semester', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mata_kuliah_semester.matakuliahsemester')),
            ],
        ),
    ]