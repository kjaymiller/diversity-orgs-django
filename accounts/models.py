"""The User Model is Slightly Complex but Ultimate Allows for some flexibility for future development."""

from django.db import models
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """This is the base user. All Users will be derived from this."""
    twitter = models.CharField(
        verbose_name = "Twitter Username",
        max_length=50, blank=True, null=True,
        help_text="(OPTIONAL) Twitter Handle Example: @kjaymiller"
    )
    github = models.CharField(
        verbose_name = "Github Username",
        max_length=200, blank=True, null=True,
        help_text="(OPTIONAL) Github Username Example: kjaymiller"
    )
    linkedin = models.URLField(
        verbose_name = "LinkedIn URL",
        max_length=200, blank=True, null=True,
        help_text="(OPTIONAL) LinkedIn URL Example: https://www.linkedin.com/in/kjaymiller"
    )

    agrees_to_coc = models.BooleanField(
        verbose_name = "I agree to the Code of Conduct",
        default=False,
    )

    def __str__(self):
        return self.username


    def __create__(self, *args, **kwargs):
        super().__create(*args, **kwargs)
        Token.objects.create(user=self)

