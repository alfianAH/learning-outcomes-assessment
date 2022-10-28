from django.contrib import admin

from .models import MyUser, Fakultas, ProgramStudi

# Register your models here.
class MyUserAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'username', 'name', 'prodi', 'role')

class FakultasAdmin(admin.ModelAdmin):
    list_display: tuple = ('id_neosia', 'nama')

class ProgramStudiAdmin(admin.ModelAdmin):
    list_display: tuple = ('id_neosia', 'nama', 'fakultas')

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Fakultas, FakultasAdmin)
admin.site.register(ProgramStudi, ProgramStudiAdmin)
