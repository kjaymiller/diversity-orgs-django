"""The User Model is Slightly Complex but Ultimate Allows for some flexibility for future development."""

from django.db import models
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """This is the base user. All Users will be derived from this."""
    twitter_handle = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="(OPTIONAL) Twitter Handle Example: @kjaymiller"
    )
    github_handle = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="(OPTIONAL) Github Username Example: kjaymiller"
    )
    linkedin_url = models.URLField(
        max_length=200, blank=True, null=True,
        help_text="(OPTIONAL) LinkedIn URL Example: https://www.linkedin.com/in/kjaymiller"
    )

    def __str__(self):
        return self.username


    def __create__(self, *args, **kwargs):
        super().__create(*args, **kwargs)
        Token.objects.create(user=self)

