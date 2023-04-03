# Generated by Django 3.2 on 2023-04-01 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lock_model', '0004_lock_is_locked'),
        ('rps', '0008_auto_20230331_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='dosenpengampurps',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
        migrations.AddField(
            model_name='durasipertemuanrps',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
        migrations.AddField(
            model_name='koordinatorrps',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
        migrations.AddField(
            model_name='matakuliahsyaratrps',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
        migrations.AddField(
            model_name='pembelajaranpertemuanrps',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
        migrations.AddField(
            model_name='pengembangrps',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
        migrations.AddField(
            model_name='pertemuanrps',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
        migrations.AddField(
            model_name='rencanapembelajaransemester',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
        migrations.AddField(
            model_name='rincianpertemuanrps',
            name='lock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lock_model.lock'),
        ),
    ]