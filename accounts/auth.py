from django.contrib.auth.backends import BaseBackend
from .models import MyUser
from .utils import validate_user

class MyBackend(BaseBackend):
    def authenticate(self, request, username, password):
        user_data = validate_user(username, password)

        if user_data is None: 
            print("User data is not valid")
            return None
        
        try:
            user = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            print("Create new user")
            user = MyUser.objects.create_new_user(user_data)
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
