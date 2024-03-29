# Generated by Django 3.2 on 2022-10-31 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0008_remove_myuser_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kurikulum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=255)),
                ('tahun_mulai', models.IntegerField(null=True)),
                ('total_sks_lulus', models.IntegerField()),
                ('is_active', models.BooleanField()),
                ('prodi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.programstudi')),
            ],
        ),
    ]
