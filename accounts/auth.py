from django.contrib.auth.backends import BaseBackend
from .models import MyUser
from .enums import RoleChoices
from .utils import validate_user

class MyBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, role=None):
        user_data = validate_user(username, password, role)

        if user_data is None: 
            print("User data is not valid")
            return None
        
        try:
            user = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            print("Create new user")
            match(role):
                case RoleChoices.ADMIN_PRODI:
                    user = MyUser.objects.create_admin_prodi_user(user_data)
                case RoleChoices.DOSEN:
                    user = MyUser.objects.create_dosen_user(user_data)
                case RoleChoices.MAHASISWA:
                    user = MyUser.objects.create_mahasiswa_user(user_data)
            
            return user

        print("Return existing user")
        return user
    
    def get_user(self, user_id):
        try:
            user = MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
        print(user)
        return user
