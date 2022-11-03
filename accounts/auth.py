from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from .models import Fakultas, MyUser, ProgramStudi
from .enums import RoleChoices
from .utils import get_user_profile

class MyBackend(BaseBackend):
    def authenticate(self, request, user=None, role=None):
        user_profile = get_user_profile(user, role)

        # Return None if user profile is None
        if user_profile is None:
            if settings.DEBUG: print("Failed to get user profile: {}".format(user['username']))
            return None

        # Get Fakultas and Program Studi from user profile
        fakultas = self.get_or_create_fakultas(user_profile)
        prodi = self.get_or_create_prodi(user_profile, fakultas)
        
        if fakultas is None or prodi is None: 
            return None
        
        # Get user
        try:
            user = MyUser.objects.get(username=user['username'])
        except MyUser.DoesNotExist:
            if settings.DEBUG: print("Create new user")
            match(role):
                case RoleChoices.ADMIN_PRODI:
                    user = MyUser.objects.create_admin_prodi_user(user, prodi)
                case RoleChoices.DOSEN:
                    user = MyUser.objects.create_dosen_user(user, prodi)
                case RoleChoices.MAHASISWA:
                    user = MyUser.objects.create_mahasiswa_user(user, prodi)
            
            return user
        except MyUser.MultipleObjectsReturned:
            if settings.DEBUG: print("MyUser returns multiple objects.")
            return None

        if settings.DEBUG: print("Return existing user")
        return user
    
    def get_user(self, user_id):
        try:
            user = MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
        if settings.DEBUG: print(user)
        return user
    
    def get_or_create_fakultas(self, user_profile: dict) -> Fakultas:
        """Get or create fakultas object

        Args:
            user_profile (dict): User's profile

        Returns:
            Fakultas: existing or new Fakultas object
        """

        try:
            fakultas = Fakultas.objects.get(id_neosia=user_profile['id_fakultas'])
        except Fakultas.DoesNotExist:
            if settings.DEBUG: print("Create new fakultas")
            fakultas = Fakultas.objects.create(
                id_neosia = user_profile['id_fakultas'],
                nama = user_profile['nama_fakultas']
            )
        except Fakultas.MultipleObjectsReturned:
            if settings.DEBUG: print("Fakultas returns multiple objects.")
            return None
        
        return fakultas
    
    def get_or_create_prodi(self, user_profile: dict, fakultas: Fakultas) -> ProgramStudi:
        """Get or create Program Studi object

        Args:
            user_profile (dict): User's profile
            fakultas (Fakultas): Fakultas foreign key

        Returns:
            ProgramStudi: existing or new Program Studi object
        """

        if fakultas is None: return None
        try:
            prodi = ProgramStudi.objects.get(
                id_neosia = user_profile['id_prodi'], 
                fakultas = fakultas
            )
        except ProgramStudi.DoesNotExist:
            if settings.DEBUG: print("Create new program studi")
            prodi = ProgramStudi.objects.create(
                id_neosia = user_profile['id_prodi'],
                fakultas = fakultas,
                nama = user_profile['nama_prodi'],
            )
        except ProgramStudi.MultipleObjectsReturned:
            if settings.DEBUG: print("Program Studi returns multiple objects.")
            return None

        return prodi
