# Generated by Django 3.2 on 2022-12-21 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pi_area', '0003_alter_assessmentarea_color'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assessmentarea',
            options={'ordering': ['nama']},
        ),
        migrations.AlterModelOptions(
            name='performanceindicatorarea',
            options={'ordering': ['pi_code']},
        ),
        migrations.CreateModel(
            name='PerformanceIndicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deskripsi', models.TextField()),
                ('pi_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pi_area.performanceindicatorarea')),
            ],
        ),
    ]
