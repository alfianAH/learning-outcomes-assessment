from django.contrib import admin

from .models import (
    Kurikulum, 
    MataKuliahKurikulum
)

# Register your models here.
class KurikulumAdmin(admin.ModelAdmin):
    list_display: tuple = ('id_neosia', 'prodi', 'nama', 'is_active')

class MataKuliahKurikulumAdmin(admin.ModelAdmin):
    list_display: tuple = ('kode', 'nama', 'prodi', 'kurikulum')

admin.site.register(Kurikulum, KurikulumAdmin)
admin.site.register(MataKuliahKurikulum, MataKuliahKurikulumAdmin)
