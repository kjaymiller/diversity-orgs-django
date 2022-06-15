"""The User Model is Slightly Complex but Ultimate Allows for some flexibility for future development."""

from django.db import models
from django.contrib.auth.models import AbstractUser
from org_pages.models import Organization

# Create your models here.
class CustomUser(AbstractUser):
    """This is the base user. All Users will be derived from this."""
    organizations = models.ManyToManyField(Organization, blank=True)

    def __str__(self):
        return self.username