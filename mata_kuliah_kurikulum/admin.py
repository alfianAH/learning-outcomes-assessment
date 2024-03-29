from django.contrib import admin
from .models import MataKuliahKurikulum


# Register your models here.
class MataKuliahKurikulumAdmin(admin.ModelAdmin):
    list_display: tuple = ('kode', 'nama', 'kurikulum')

admin.site.register(MataKuliahKurikulum, MataKuliahKurikulumAdmin)
