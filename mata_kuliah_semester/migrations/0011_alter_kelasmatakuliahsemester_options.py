# Generated by Django 3.2 on 2023-01-18 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0010_remove_kelasmatakuliahsemester_kelas'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kelasmatakuliahsemester',
            options={'ordering': ['nama']},
        ),
    ]
