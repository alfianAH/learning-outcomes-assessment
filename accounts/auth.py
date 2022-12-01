from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from .models import Fakultas, MyUser, ProgramStudi
from .enums import RoleChoices
from .utils import (
    get_user_profile,
    validate_mahasiswa,
)

class MyBackend(BaseBackend):
    def authenticate(self, request, user=None, password: str = None, role: RoleChoices = None):
        """Authenticate user

        Args:
            request (HttpRequest): 
            user (str or dict, optional): user is user data (dictionary) for Dosen and Admin Prodi. user is username (str) for Mahasiswa. Defaults to None.
            password (str, optional): Password for mahasiswa form. Defaults to None.
            role (RoleChoices, optional): User's role. Defaults to None.

        Returns:
            MyUser: User object if succesfully gotten or created else None
        """
        match(role):
            case RoleChoices.ADMIN_PRODI:
                user_data = {
                    'username': user['nip'],
                    'nama': user['nama'],
                    'id_prodi': user['prodi']['id'],
                    'nama_prodi': user['prodi']['nama_resmi'],
                }

                # Get Program Studi
                prodi = self.get_or_create_prodi(
                    user_data['id_prodi'], 
                    user_data['nama_prodi']
                )
            case RoleChoices.DOSEN:
                user_data = {
                    'username': user['nip'],
                    'nama': user['nama'],
                }

                user_profile = get_user_profile(user, role)
            case RoleChoices.MAHASISWA:
                user_data = validate_mahasiswa(user, password)

                # Return None if user data is None
                if user_data is None: 
                    if settings.DEBUG: print("User data is not valid: {}".format(user))
                    return None
                
                user_profile = get_user_profile(user, role)

                # Return None if user profile is None
                if user_profile is None:
                    if settings.DEBUG: print("Failed to get user profile: {}".format(user['username']))
                    return None

                # Get Fakultas and Program Studi from user profile
                fakultas = self.get_or_create_fakultas(
                    user_profile['id_fakultas'], 
                    user_profile['nama_fakultas']
                )
                prodi = self.get_or_create_prodi(
                    user_profile['id_prodi'], 
                    user_profile['nama_prodi'], 
                    fakultas
                )
                
                if fakultas is None or prodi is None: 
                    return None
        
        # Get user
        try:
            if role == RoleChoices.MAHASISWA:
                user_obj = MyUser.objects.get(username=user)
            else:
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
    
    def get_or_create_fakultas(self, id_fakultas: int, nama_fakultas: str) -> Fakultas:
        """Get or create fakultas object

        Args:
            id_fakultas (int): Fakultas' ID
            nama_fakultas (str): Fakultas' name

        Returns:
            Fakultas: existing or new Fakultas object
        """

        try:
            fakultas = Fakultas.objects.get(id_neosia=id_fakultas)
        except Fakultas.DoesNotExist:
            if settings.DEBUG: print("Create new fakultas")
            fakultas = Fakultas.objects.create(
                id_neosia = id_fakultas,
                nama = nama_fakultas
            )
        except Fakultas.MultipleObjectsReturned:
            if settings.DEBUG: print("Fakultas returns multiple objects.")
            return None
        
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
