from django.contrib.auth.backends import BaseBackend
from .models import MyUser

class MyBackend(BaseBackend):
    def authenticate(self, request, user):
        print("Authenticate")
        find_user = MyUser.objects.filter(username=user['nim'])
        if len(find_user) == 0:
            print("User not found. Save new user...")
            new_user = MyUser.objects.create_new_user(user)
            print(new_user)
            return new_user
        
        print("User was found. Returning")
        return find_user[0]
