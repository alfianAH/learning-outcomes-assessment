from django.contrib.auth.models import Group, Permission

admin_prodi_group, admin_created = Group.objects.get_or_create(name='Admin Program Studi')
dosen_group, dosen_created = Group.objects.get_or_create(name='Dosen')
mahasiswa_group, mahasiswa_created = Group.objects.get_or_create(name='Mahasiswa')

admin_prodi_permissions = [
    'accounts.add_fakultas',
    'accounts.change_fakultas',
    'accounts.delete_fakultas',
    'accounts.view_fakultas',

    'accounts.add_jenjangstudi',
    'accounts.change_jenjangstudi',
    'accounts.delete_jenjangstudi',
    'accounts.view_jenjangstudi',

    'accounts.add_myuser',
    'accounts.change_myuser',
    'accounts.delete_myuser',
    'accounts.view_myuser',

    'accounts.add_programstudi',
    'accounts.change_programstudi',
    'accounts.delete_programstudi',
    'accounts.view_programstudi',

    'accounts.add_programstudijenjang',
    'accounts.change_programstudijenjang',
    'accounts.delete_programstudijenjang',
    'accounts.view_programstudijenjang',

    'clo.add_clo',
    'clo.change_clo',
    'clo.delete_clo',
    'clo.view_clo',

    'clo.add_komponenclo',
    'clo.change_komponenclo',
    'clo.delete_komponenclo',
    'clo.view_komponenclo',

    'clo.add_nilaiclomatakuliahsemester',
    'clo.change_nilaiclomatakuliahsemester',
    'clo.delete_nilaiclomatakuliahsemester',
    'clo.view_nilaiclomatakuliahsemester',

    'clo.add_nilaiclopeserta',
    'clo.change_nilaiclopeserta',
    'clo.delete_nilaiclopeserta',
    'clo.view_nilaiclopeserta',

    'clo.add_nilaikomponenclopeserta',
    'clo.change_nilaikomponenclopeserta',
    'clo.delete_nilaikomponenclopeserta',
    'clo.view_nilaikomponenclopeserta',

    'clo.add_piclo',
    'clo.change_piclo',
    'clo.delete_piclo',
    'clo.view_piclo',

    'ilo.add_ilo',
    'ilo.change_ilo',
    'ilo.delete_ilo',
    'ilo.view_ilo',

    'kurikulum.add_kurikulum',
    'kurikulum.change_kurikulum',
    'kurikulum.delete_kurikulum',
    'kurikulum.view_kurikulum',

    'mata_kuliah_kurikulum.add_matakuliahkurikulum',
    'mata_kuliah_kurikulum.change_matakuliahkurikulum',
    'mata_kuliah_kurikulum.delete_matakuliahkurikulum',
    'mata_kuliah_kurikulum.view_matakuliahkurikulum',

    'lock_model.add_lock',
    'lock_model.change_lock',
    'lock_model.delete_lock',
    'lock_model.view_lock',

    'mata_kuliah_semester.add_dosenmatakuliah',
    'mata_kuliah_semester.change_dosenmatakuliah',
    'mata_kuliah_semester.delete_dosenmatakuliah',
    'mata_kuliah_semester.view_dosenmatakuliah',

    'mata_kuliah_semester.add_kelasmatakuliahsemester',
    'mata_kuliah_semester.change_kelasmatakuliahsemester',
    'mata_kuliah_semester.delete_kelasmatakuliahsemester',
    'mata_kuliah_semester.view_kelasmatakuliahsemester',

    'mata_kuliah_semester.add_matakuliahsemester',
    'mata_kuliah_semester.change_matakuliahsemester',
    'mata_kuliah_semester.delete_matakuliahsemester',
    'mata_kuliah_semester.view_matakuliahsemester',

    'mata_kuliah_semester.add_nilaiexcelmatakuliahsemester',
    'mata_kuliah_semester.change_nilaiexcelmatakuliahsemester',
    'mata_kuliah_semester.delete_nilaiexcelmatakuliahsemester',
    'mata_kuliah_semester.view_nilaiexcelmatakuliahsemester',

    'mata_kuliah_semester.add_nilaimatakuliahilomahasiswa',
    'mata_kuliah_semester.change_nilaimatakuliahilomahasiswa',
    'mata_kuliah_semester.delete_nilaimatakuliahilomahasiswa',
    'mata_kuliah_semester.view_nilaimatakuliahilomahasiswa',

    'mata_kuliah_semester.add_pesertamatakuliah',
    'mata_kuliah_semester.change_pesertamatakuliah',
    'mata_kuliah_semester.delete_pesertamatakuliah',
    'mata_kuliah_semester.view_pesertamatakuliah',

    'pi_area.add_performanceindicator',
    'pi_area.change_performanceindicator',
    'pi_area.delete_performanceindicator',
    'pi_area.view_performanceindicator',

    'pi_area.add_assessmentarea',
    'pi_area.change_assessmentarea',
    'pi_area.delete_assessmentarea',
    'pi_area.view_assessmentarea',

    'pi_area.add_performanceindicatorarea',
    'pi_area.change_performanceindicatorarea',
    'pi_area.delete_performanceindicatorarea',
    'pi_area.view_performanceindicatorarea',

    'rps.add_rencanapembelajaransemester',
    'rps.change_rencanapembelajaransemester',
    'rps.delete_rencanapembelajaransemester',
    'rps.view_rencanapembelajaransemester',

    'semester.add_semester',
    'semester.change_semester',
    'semester.delete_semester',
    'semester.view_semester',

    'semester.add_semesterprodi',
    'semester.change_semesterprodi',
    'semester.delete_semesterprodi',
    'semester.view_semesterprodi',

    'semester.add_tahunajaran',
    'semester.change_tahunajaran',
    'semester.delete_tahunajaran',
    'semester.view_tahunajaran',

    'semester.add_tahunajaranprodi',
    'semester.change_tahunajaranprodi',
    'semester.delete_tahunajaranprodi',
    'semester.view_tahunajaranprodi',
]

dosen_permissions = [
    'accounts.view_programstudijenjang',

    'clo.add_clo',
    'clo.change_clo',
    'clo.delete_clo',
    'clo.view_clo',

    'clo.add_komponenclo',
    'clo.change_komponenclo',
    'clo.delete_komponenclo',
    'clo.view_komponenclo',

    'clo.add_nilaiclomatakuliahsemester',
    'clo.change_nilaiclomatakuliahsemester',
    'clo.delete_nilaiclomatakuliahsemester',
    'clo.view_nilaiclomatakuliahsemester',

    'clo.add_nilaiclopeserta',
    'clo.change_nilaiclopeserta',
    'clo.delete_nilaiclopeserta',
    'clo.view_nilaiclopeserta',

    'clo.add_nilaikomponenclopeserta',
    'clo.change_nilaikomponenclopeserta',
    'clo.delete_nilaikomponenclopeserta',
    'clo.view_nilaikomponenclopeserta',

    'clo.add_piclo',
    'clo.change_piclo',
    'clo.delete_piclo',
    'clo.view_piclo',

    'ilo.add_ilo',
    'ilo.change_ilo',
    'ilo.delete_ilo',
    'ilo.view_ilo',
    
    'kurikulum.change_kurikulum',
    'kurikulum.view_kurikulum',

    'mata_kuliah_kurikulum.add_matakuliahkurikulum',
    'mata_kuliah_kurikulum.change_matakuliahkurikulum',
    'mata_kuliah_kurikulum.delete_matakuliahkurikulum',
    'mata_kuliah_kurikulum.view_matakuliahkurikulum',

    'lock_model.add_lock',
    'lock_model.change_lock',
    'lock_model.delete_lock',
    'lock_model.view_lock',

    'mata_kuliah_semester.add_dosenmatakuliah',
    'mata_kuliah_semester.change_dosenmatakuliah',
    'mata_kuliah_semester.delete_dosenmatakuliah',
    'mata_kuliah_semester.view_dosenmatakuliah',

    'mata_kuliah_semester.add_kelasmatakuliahsemester',
    'mata_kuliah_semester.change_kelasmatakuliahsemester',
    'mata_kuliah_semester.delete_kelasmatakuliahsemester',
    'mata_kuliah_semester.view_kelasmatakuliahsemester',

    'mata_kuliah_semester.add_matakuliahsemester',
    'mata_kuliah_semester.change_matakuliahsemester',
    'mata_kuliah_semester.delete_matakuliahsemester',
    'mata_kuliah_semester.view_matakuliahsemester',

    'mata_kuliah_semester.add_nilaiexcelmatakuliahsemester',
    'mata_kuliah_semester.change_nilaiexcelmatakuliahsemester',
    'mata_kuliah_semester.delete_nilaiexcelmatakuliahsemester',
    'mata_kuliah_semester.view_nilaiexcelmatakuliahsemester',

    'mata_kuliah_semester.add_nilaimatakuliahilomahasiswa',
    'mata_kuliah_semester.change_nilaimatakuliahilomahasiswa',
    'mata_kuliah_semester.delete_nilaimatakuliahilomahasiswa',
    'mata_kuliah_semester.view_nilaimatakuliahilomahasiswa',

    'mata_kuliah_semester.add_pesertamatakuliah',
    'mata_kuliah_semester.change_pesertamatakuliah',
    'mata_kuliah_semester.delete_pesertamatakuliah',
    'mata_kuliah_semester.view_pesertamatakuliah',

    'pi_area.add_performanceindicator',
    'pi_area.change_performanceindicator',
    'pi_area.delete_performanceindicator',
    'pi_area.view_performanceindicator',

    'pi_area.add_assessmentarea',
    'pi_area.change_assessmentarea',
    'pi_area.delete_assessmentarea',
    'pi_area.view_assessmentarea',

    'pi_area.add_performanceindicatorarea',
    'pi_area.change_performanceindicatorarea',
    'pi_area.delete_performanceindicatorarea',
    'pi_area.view_performanceindicatorarea',

    'rps.add_rencanapembelajaransemester',
    'rps.change_rencanapembelajaransemester',
    'rps.delete_rencanapembelajaransemester',
    'rps.view_rencanapembelajaransemester',

    'semester.view_semester',
    
    'semester.view_semesterprodi',
    
    'semester.view_tahunajaran',

    'semester.view_tahunajaranprodi',
]

mahasiswa_permissions = [
    'clo.view_clo',
    'clo.view_komponenclo',
    
    'clo.add_nilaiclopeserta',
    'clo.change_nilaiclopeserta',
    'clo.view_nilaiclopeserta',

    'clo.view_nilaikomponenclopeserta',
    'clo.view_piclo',
    'clo.view_nilaiclomatakuliahsemester',
    'ilo.view_ilo',
    'kurikulum.view_kurikulum',
    'mata_kuliah_kurikulum.view_matakuliahkurikulum',
    'lock_model.view_lock',
    'mata_kuliah_semester.view_dosenmatakuliah',
    'mata_kuliah_semester.view_kelasmatakuliahsemester',
    'mata_kuliah_semester.view_matakuliahsemester',

    'mata_kuliah_semester.add_nilaimatakuliahilomahasiswa',
    'mata_kuliah_semester.change_nilaimatakuliahilomahasiswa',
    'mata_kuliah_semester.view_nilaimatakuliahilomahasiswa',
    
    'mata_kuliah_semester.view_pesertamatakuliah',
    'pi_area.view_performanceindicator',
    'pi_area.view_assessmentarea',
    'pi_area.view_performanceindicatorarea',
    'rps.view_rencanapembelajaransemester',
    'semester.view_semester',
    'semester.view_semesterprodi',
    'semester.view_tahunajaran',
    'semester.view_tahunajaranprodi',
]

def set_permissions(group, permissions):
    for permission in permissions:
        app_label, permission_codename = permission.split('.')
        try:
            permission = Permission.objects.get(
                content_type__app_label=app_label,
                codename=permission_codename,
            )
        except Permission.MultipleObjectsReturned:
            print('Multi object found: {}'.format(permission))
            continue
        except Permission.DoesNotExist:
            print('Does not exist: {}'.format(permission))
            continue
        
        group.permissions.add(permission)


set_permissions(admin_prodi_group, admin_prodi_permissions)
set_permissions(dosen_group, dosen_permissions)
set_permissions(mahasiswa_group, mahasiswa_permissions)
