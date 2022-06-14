"""The User Model is Slightly Complex but Ultimate Allows for some flexibility for future development."""

from django.db import models
from django.contrib.auth.models import AbstractUser
import org_pages.models

# Create your models here.
class CustomUser(AbstractUser):
    """This is the base user. All Users will be derived from this."""
    is_organizer = models.BooleanField(default=False)

    class Meta:
        db_table = 'auth_user'
    
    def __str__(self):
        return self.username

class APIUser(models.Model):
    """Establish API access to base API requests. 
    NOTE: In the future, some users will not have this by default. (Folks attending user groups)"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    organizations = models.ManyToManyField(org_pages.models.Organization, blank=True, related_name='api_users_organizations')