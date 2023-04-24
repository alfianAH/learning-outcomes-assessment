from django.contrib.auth.models import Group, Permission

admin_prodi_group, admin_created = Group.objects.get_or_create(name='Admin Program Studi')
dosen_group, dosen_created = Group.objects.get_or_create(name='Dosen')
mahasiswa_group, mahasiswa_created = Group.objects.get_or_create(name='Mahasiswa')

admin_prodi_permissions = [
    'add_fakultas',
    'change_fakultas',
    'delete_fakultas',
    'view_fakultas',

    'add_jenjangstudi',
    'change_jenjangstudi',
    'delete_jenjangstudi',
    'view_jenjangstudi',

    'add_myuser',
    'change_myuser',
    'delete_myuser',
    'view_myuser',

    'add_programstudi',
    'change_programstudi',
    'delete_programstudi',
    'view_programstudi',

    'add_programstudijenjang',
    'change_programstudijenjang',
    'delete_programstudijenjang',
    'view_programstudijenjang',

    'add_clo',
    'change_clo',
    'delete_clo',
    'view_clo',

    'add_komponenclo',
    'change_komponenclo',
    'delete_komponenclo',
    'view_komponenclo',

    'add_nilaiclomatakuliahsemester',
    'change_nilaiclomatakuliahsemester',
    'delete_nilaiclomatakuliahsemester',
    'view_nilaiclomatakuliahsemester',

    'add_nilaiclopeserta',
    'change_nilaiclopeserta',
    'delete_nilaiclopeserta',
    'view_nilaiclopeserta',

    'add_nilaikomponenclopeserta',
    'change_nilaikomponenclopeserta',
    'delete_nilaikomponenclopeserta',
    'view_nilaikomponenclopeserta',

    'add_piclo',
    'change_piclo',
    'delete_piclo',
    'view_piclo',

    'add_ilo',
    'change_ilo',
    'delete_ilo',
    'view_ilo',

    'add_kurikulum',
    'change_kurikulum',
    'delete_kurikulum',
    'view_kurikulum',

    'add_matakuliahkurikulum',
    'change_matakuliahkurikulum',
    'delete_matakuliahkurikulum',
    'view_matakuliahkurikulum',

    'add_lock',
    'change_lock',
    'delete_lock',
    'view_lock',

    'add_dosenmatakuliah',
    'change_dosenmatakuliah',
    'delete_dosenmatakuliah',
    'view_dosenmatakuliah',

    'add_kelasmatakuliahsemester',
    'change_kelasmatakuliahsemester',
    'delete_kelasmatakuliahsemester',
    'view_kelasmatakuliahsemester',

    'add_matakuliahsemester',
    'change_matakuliahsemester',
    'delete_matakuliahsemester',
    'view_matakuliahsemester',

    'add_nilaiexcelmatakuliahsemester',
    'change_nilaiexcelmatakuliahsemester',
    'delete_nilaiexcelmatakuliahsemester',
    'view_nilaiexcelmatakuliahsemester',

    'add_nilaimatakuliahilomahasiswa',
    'change_nilaimatakuliahilomahasiswa',
    'delete_nilaimatakuliahilomahasiswa',
    'view_nilaimatakuliahilomahasiswa',

    'add_pesertamatakuliah',
    'change_pesertamatakuliah',
    'delete_pesertamatakuliah',
    'view_pesertamatakuliah',

    'add_performanceindicator',
    'change_performanceindicator',
    'delete_performanceindicator',
    'view_performanceindicator',

    'add_assessmentarea',
    'change_assessmentarea',
    'delete_assessmentarea',
    'view_assessmentarea',

    'add_performanceindicatorarea',
    'change_performanceindicatorarea',
    'delete_performanceindicatorarea',
    'view_performanceindicatorarea',

    'add_rencanapembelajaransemester',
    'change_rencanapembelajaransemester',
    'delete_rencanapembelajaransemester',
    'view_rencanapembelajaransemester',

    'add_semester',
    'change_semester',
    'delete_semester',
    'view_semester',

    'add_semesterprodi',
    'change_semesterprodi',
    'delete_semesterprodi',
    'view_semesterprodi',

    'add_tahunajaran',
    'change_tahunajaran',
    'delete_tahunajaran',
    'view_tahunajaran',

    'add_tahunajaranprodi',
    'change_tahunajaranprodi',
    'delete_tahunajaranprodi',
    'view_tahunajaranprodi',
]

dosen_permissions = [
    'view_programstudijenjang',

    'add_clo',
    'change_clo',
    'delete_clo',
    'view_clo',

    'add_komponenclo',
    'change_komponenclo',
    'delete_komponenclo',
    'view_komponenclo',

    'add_nilaiclomatakuliahsemester',
    'change_nilaiclomatakuliahsemester',
    'delete_nilaiclomatakuliahsemester',
    'view_nilaiclomatakuliahsemester',

    'add_nilaiclopeserta',
    'change_nilaiclopeserta',
    'delete_nilaiclopeserta',
    'view_nilaiclopeserta',

    'add_nilaikomponenclopeserta',
    'change_nilaikomponenclopeserta',
    'delete_nilaikomponenclopeserta',
    'view_nilaikomponenclopeserta',

    'add_piclo',
    'change_piclo',
    'delete_piclo',
    'view_piclo',

    'add_ilo',
    'change_ilo',
    'delete_ilo',
    'view_ilo',
    
    'view_kurikulum',

    'add_matakuliahkurikulum',
    'change_matakuliahkurikulum',
    'delete_matakuliahkurikulum',
    'view_matakuliahkurikulum',

    'add_lock',
    'change_lock',
    'delete_lock',
    'view_lock',

    'add_dosenmatakuliah',
    'change_dosenmatakuliah',
    'delete_dosenmatakuliah',
    'view_dosenmatakuliah',

    'add_kelasmatakuliahsemester',
    'change_kelasmatakuliahsemester',
    'delete_kelasmatakuliahsemester',
    'view_kelasmatakuliahsemester',

    'add_matakuliahsemester',
    'change_matakuliahsemester',
    'delete_matakuliahsemester',
    'view_matakuliahsemester',

    'add_nilaiexcelmatakuliahsemester',
    'change_nilaiexcelmatakuliahsemester',
    'delete_nilaiexcelmatakuliahsemester',
    'view_nilaiexcelmatakuliahsemester',

    'add_nilaimatakuliahilomahasiswa',
    'change_nilaimatakuliahilomahasiswa',
    'delete_nilaimatakuliahilomahasiswa',
    'view_nilaimatakuliahilomahasiswa',

    'add_pesertamatakuliah',
    'change_pesertamatakuliah',
    'delete_pesertamatakuliah',
    'view_pesertamatakuliah',

    'add_performanceindicator',
    'change_performanceindicator',
    'delete_performanceindicator',
    'view_performanceindicator',

    'add_assessmentarea',
    'change_assessmentarea',
    'delete_assessmentarea',
    'view_assessmentarea',

    'add_performanceindicatorarea',
    'change_performanceindicatorarea',
    'delete_performanceindicatorarea',
    'view_performanceindicatorarea',

    'add_rencanapembelajaransemester',
    'change_rencanapembelajaransemester',
    'delete_rencanapembelajaransemester',
    'view_rencanapembelajaransemester',

    'view_semester',
    
    'view_semesterprodi',
    
    'view_tahunajaran',

    'view_tahunajaranprodi',
]

mahasiswa_permissions = [
    'view_clo',
    'view_komponenclo',
    'view_nilaiclopeserta',
    'view_nilaikomponenclopeserta',
    'view_piclo',
    'view_ilo',
    'view_kurikulum',
    'view_matakuliahkurikulum',
    'view_lock',
    'view_dosenmatakuliah',
    'view_kelasmatakuliahsemester',
    'view_matakuliahsemester',
    'view_nilaimatakuliahilomahasiswa',
    'view_pesertamatakuliah',
    'view_performanceindicator',
    'view_assessmentarea',
    'view_performanceindicatorarea',
    'view_rencanapembelajaransemester',
    'view_semester',
    'view_semesterprodi',
    'view_tahunajaran',
    'view_tahunajaranprodi',
]

def set_permissions(group, permissions):
    for permission in permissions:
        try:
            permission = Permission.objects.get(codename=permission)
        except Permission.MultipleObjectsReturned:
            print('Multi object found: {}'.format(permission))
            permission = Permission.objects.filter(codename=permission).first()
        except Permission.DoesNotExist:
            print('Does not exist: {}'.format(permission))
            continue
        
        group.permissions.add(permission)


set_permissions(admin_prodi_group, admin_prodi_permissions)
set_permissions(dosen_group, dosen_permissions)
set_permissions(mahasiswa_group, mahasiswa_permissions)
