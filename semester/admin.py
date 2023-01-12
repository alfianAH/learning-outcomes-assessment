from django.contrib import admin
from .models import (
    TahunAjaran,
    TahunAjaranProdi,
    Semester,
    SemesterProdi,
)


# Register your models here.
admin.site.register([TahunAjaran, TahunAjaranProdi, Semester, SemesterProdi])