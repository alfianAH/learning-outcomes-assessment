from django.contrib import admin

from .models import Kurikulum

# Register your models here.
class KurikulumAdmin(admin.ModelAdmin):
    list_display: tuple = ('id_neosia', 'prodi_jenjang', 'nama', 'is_active')

admin.site.register(Kurikulum, KurikulumAdmin)
