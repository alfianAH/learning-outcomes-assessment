from django.contrib.auth.models import Group, Permission

admin_prodi_group, admin_created = Group.objects.get_or_create(name='Admin Program Studi')
dosen_group, dosen_created = Group.objects.get_or_create(name='Dosen')
mahasiswa_group, mahasiswa_created = Group.objects.get_or_create(name='Mahasiswa')

admin_prodi_permissions = [
    # Kurikulum
    'add_kurikulum',
    'change_kurikulum',
    'delete_kurikulum',
    'view_kurikulum',

    # Mata kuliah kurikulum
    'add_matakuliahkurikulum',
    'change_matakuliahkurikulum',
    'delete_matakuliahkurikulum',
    'view_matakuliahkurikulum',

    # Assessment Area
    'add_assessmentarea',
    'change_assessmentarea',
    'delete_assessmentarea',
    'view_assessmentarea',

    # Performance Indicator Area
    'add_performanceindicatorarea',
    'change_performanceindicatorarea',
    'delete_performanceindicatorarea',
    'view_performanceindicatorarea',

    # Performance Indicator
    'add_performanceindicator',
    'change_performanceindicator',
    'delete_performanceindicator',
    'view_performanceindicator',

    # ILO
    'add_ilo',
    'change_ilo',
    'delete_ilo',
    'view_ilo',

    # Mata Kuliah Semester
    'add_matakuliahsemester',
    'change_matakuliahsemester',
    'delete_matakuliahsemester',
    'view_matakuliahsemester',

    # Kelas Mata Kuliah Semester
    'add_kelasmatakuliahsemester',
    'change_kelasmatakuliahsemester',
    'delete_kelasmatakuliahsemester',
    'view_kelasmatakuliahsemester',

    # Dosen Mata Kuliah
    'add_dosenmatakuliah',
    'change_dosenmatakuliah',
    'delete_dosenmatakuliah',
    'view_dosenmatakuliah',
]

dosen_permissions = [
    # Kurikulum
    'add_kurikulum',
    'change_kurikulum',
    'delete_kurikulum',
    'view_kurikulum',

    # Mata kuliah kurikulum
    'add_matakuliahkurikulum',
    'change_matakuliahkurikulum',
    'delete_matakuliahkurikulum',
    'view_matakuliahkurikulum',

    # Assessment Area
    'add_assessmentarea',
    'change_assessmentarea',
    'delete_assessmentarea',
    'view_assessmentarea',

    # Performance Indicator Area
    'add_performanceindicatorarea',
    'change_performanceindicatorarea',
    'delete_performanceindicatorarea',
    'view_performanceindicatorarea',

    # Performance Indicator
    'add_performanceindicator',
    'change_performanceindicator',
    'delete_performanceindicator',
    'view_performanceindicator',

    # ILO
    'add_ilo',
    'change_ilo',
    'delete_ilo',
    'view_ilo',

    # Mata Kuliah Semester
    'add_matakuliahsemester',
    'change_matakuliahsemester',
    'delete_matakuliahsemester',
    'view_matakuliahsemester',

    # Kelas Mata Kuliah Semester
    'add_kelasmatakuliahsemester',
    'change_kelasmatakuliahsemester',
    'delete_kelasmatakuliahsemester',
    'view_kelasmatakuliahsemester',

    # Dosen Mata Kuliah
    'add_dosenmatakuliah',
    'change_dosenmatakuliah',
    'delete_dosenmatakuliah',
    'view_dosenmatakuliah',
]

mahasiswa_permissions = [
]

def set_permissions(group, permissions):
    for permission in permissions:
        permission = Permission.objects.get(codename=permission)
        group.permissions.add(permission)


set_permissions(admin_prodi_group, admin_prodi_permissions)
set_permissions(dosen_group, dosen_permissions)
set_permissions(mahasiswa_group, mahasiswa_permissions)
