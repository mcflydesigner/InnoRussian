from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model

class CustomBackend(ModelBackend):
    """
        Custom backend for this project for authentication of the user.
        All functions are implemented following the recommendations from the
        django doc.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()

        try:
            user = User.objects.get(email=username)
            password_valid = check_password(password, user.password)

            if password_valid:
                return user
        except User.DoesNotExist:
            pass

        return None


    def get_user(self, user_id):
        User = get_user_model()

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None