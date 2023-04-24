from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from learning_outcomes_assessment.utils import request_data_to_neosia
from django.contrib.auth.models import Permission
from .models import (
    Fakultas, MyUser, ProgramStudi,
)
from .enums import RoleChoices
from .utils import (
    get_user_profile,
)


DETAIL_FAKULTAS_URL = 'https://customapi.neosia.unhas.ac.id/getDetilFakultas'

class MyBackend(BaseBackend):
    def authenticate(self, request, user=None, role: RoleChoices = None):
        """Authenticate user

        Args:
            request (HttpRequest): 
            user (dict, optional): user is user data (dictionary) for Dosen, Admin Prodi, Mahasiswa. Defaults to None.
            role (RoleChoices, optional): User's role. Defaults to None.

        Returns:
            MyUser: User object if succesfully gotten or created else None
        """
        prodi = None
        
        if role == RoleChoices.ADMIN_PRODI or role == RoleChoices.DOSEN:
            user_data = {
                'username': user['nip'],
                'nama': user['nama'],
            }

            # Get prodi from Neosia
            if user.get('prodi') is None:
                user_profile = get_user_profile(user_data, role)
                
                # Return None if user profile is None
                if user_profile is None:
                    if settings.DEBUG: print("Failed to get user profile: {}".format(user_data['username']))
                else:
                    _, prodi = self.get_or_create_fakultas_and_prodi_from_neosia(user_profile)
            # Get Prodi from MBerkas
            else:
                user_data.update({
                    'id_prodi': user['prodi']['id'],
                    'nama_prodi': user['prodi']['nama_resmi'],
                    'id_fakultas': user['prodi']['id_fakultas']
                })

                _, prodi = self.get_or_create_fakultas_and_prodi_from_mberkas(user_data)
        elif role == RoleChoices.MAHASISWA:
            user_data = user
            user_profile = get_user_profile(user_data, role)
            
            if user_profile is None:
                if settings.DEBUG: print("Failed to get user profile: {}".format(user['username']))
            else:
                _, prodi = self.get_or_create_fakultas_and_prodi_from_neosia(user_profile)

        # Get user
        try:
            user_obj = MyUser.objects.get(username=user_data['username'])
        except MyUser.DoesNotExist:
            if settings.DEBUG: print("Create new user")
            match(role):
                case RoleChoices.ADMIN_PRODI:
                    user_obj = MyUser.objects.create_admin_prodi_user(user_data, prodi)
                case RoleChoices.DOSEN:
                    user_obj = MyUser.objects.create_dosen_user(user_data, prodi)
                case RoleChoices.MAHASISWA:
                    user_obj = MyUser.objects.create_mahasiswa_user(user_data, prodi)
            
            return user_obj
        except MyUser.MultipleObjectsReturned:
            if settings.DEBUG: print("MyUser returns multiple objects.")
            return None

        if settings.DEBUG: print("Return existing user")
        return user_obj
    
    def get_user(self, user_id):
        try:
            user = MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
        if settings.DEBUG: print(user)
        return user
    
    def _get_user_permissions(self, user_obj):
        return user_obj.user_permissions.all()

    def _get_group_permissions(self, user_obj):
        user_groups_field = MyUser._meta.get_field('groups')
        user_groups_query = 'group__%s' % user_groups_field.related_query_name()
        return Permission.objects.filter(**{user_groups_query: user_obj})

    def _get_permissions(self, user_obj, obj, from_name):
        """
        Return the permissions of `user_obj` from `from_name`. `from_name` can
        be either "group" or "user" to return permissions from
        `_get_group_permissions` or `_get_user_permissions` respectively.
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = '_%s_perm_cache' % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, '_get_%s_permissions' % from_name)(user_obj)
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            setattr(user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})
        return getattr(user_obj, perm_cache_name)

    def get_user_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from their
        `user_permissions`.
        """
        return self._get_permissions(user_obj, obj, 'user')

    def get_group_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from the
        groups they belong.
        """
        return self._get_permissions(user_obj, obj, 'group')

    def get_or_create_fakultas_and_prodi_from_mberkas(self, user_data: dict):
        """Get or create fakultas and prodi from MBerkas user data

        Args:
            user_data (dict): User data from MBerkas

        Returns:
            tuple: Fakultas and Program Studi
        """
        
        detail_fakultas = request_data_to_neosia(DETAIL_FAKULTAS_URL, params={
            'id': user_data['id_fakultas']
        })
        fakultas = None
        
        if detail_fakultas is not None or len(detail_fakultas) > 0:
            # Get Fakultas
            fakultas = self.get_or_create_fakultas(
                user_data['id_fakultas'],
                detail_fakultas[0]['nama_resmi']
            )
        
        # Get Program Studi
        prodi = self.get_or_create_prodi(
            user_data['id_prodi'], 
            user_data['nama_prodi'],
            fakultas
        )

        return fakultas, prodi

    def get_or_create_fakultas_and_prodi_from_neosia(self, user_profile: dict):
        """Get or create fakultas and prodi from Neosia user profile

        Args:
            user_profile (dict): User profile from Neosia

        Returns:
            tuple: Fakultas and Program Studi
        """
        
        # 'nama_fakultas' is mahasiswa profile from Neosia
        # Get Fakultas and Program Studi from user profile
        nama_fakultas = user_profile.get('nama_fakultas')
        if nama_fakultas is not None:
            fakultas = self.get_or_create_fakultas(
                user_profile['id_fakultas'], 
                nama_fakultas
            )
        else:
            # 'nama_resmi' is dosen profile from Neosia
            nama_fakultas = user_profile.get('nama_resmi')
            fakultas = self.get_or_create_fakultas(
                user_profile['id_fakultas'], 
                nama_fakultas
            )
        
        prodi = self.get_or_create_prodi(
            user_profile['id_prodi'], 
            user_profile['nama_prodi'], 
            fakultas
        )

        return fakultas, prodi
    
    def get_or_create_fakultas(self, id_fakultas: int, nama_fakultas: str) -> Fakultas:
        """Get or create fakultas object

        Args:
            id_fakultas (int): Fakultas' ID
            nama_fakultas (str): Fakultas' name

        Returns:
            Fakultas: existing or new Fakultas object
        """

        fakultas, _ = Fakultas.objects.get_or_create(
            id_neosia=id_fakultas,
            nama=nama_fakultas
        )
        
        return fakultas
    
    def get_or_create_prodi(self, id_prodi: int, nama_prodi: str, fakultas: Fakultas = None) -> ProgramStudi:
        """Get or create Program Studi object

        Args:
            id_prodi (int): Program Studi ID
            nama_prodi (str): Program Studi Name
            fakultas (Fakultas): Fakultas foreign key

        Returns:
            ProgramStudi: existing or new Program Studi object
        """

        try:
            prodi = ProgramStudi.objects.get(
                id_neosia = id_prodi,
            )
        except ProgramStudi.DoesNotExist:
            if settings.DEBUG: print("Create new program studi")
            prodi = ProgramStudi.objects.create(
                id_neosia = id_prodi,
                fakultas = fakultas,
                nama = nama_prodi,
            )
        except ProgramStudi.MultipleObjectsReturned:
            if settings.DEBUG: print("Program Studi returns multiple objects.")
            return None

        if fakultas is not None:
            if prodi.fakultas is None:
                prodi.fakultas = fakultas
                
        return prodi
