from django.db import models
from django.urls import reverse

# Create your models here.

class ParentOrganization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    social_links = models.TextField(blank=True)
    events_link = models.URLField(blank=True)
    online_only = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('org_detail', kwrgs={'pk': self.pk})

class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    social_links = models.TextField(blank=True)
    events_link = models.URLField(blank=True)
    online_only = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    parent = models.ForeignKey(ParentOrganization, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('org_detail', kwrgs={'pk': self.pk})

