from django.contrib.auth.backends import ModelBackend
from .models import Accounts

class EmailBackend(ModelBackend):
    """Authenticate using email instead of username"""

    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Accounts.objects.get(email=email)
        except Accounts.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
