"""The User Model is Slightly Complex but Ultimate Allows for some flexibility for future development."""

from django.db import models
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """This is the base user. All Users will be derived from this."""
    def __str__(self):
        return self.username


    def __create__(self, *args, **kwargs):
        super().__create(*args, **kwargs)
        Token.objects.create(user=self)

