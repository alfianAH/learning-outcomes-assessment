# Generated by Django 3.2 on 2023-02-27 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mata_kuliah_semester', '0018_delete_averagecloachievementmatakuliahsemester'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesertamatakuliah',
            name='status_nilai',
            field=models.BooleanField(default=False),
        ),
    ]
