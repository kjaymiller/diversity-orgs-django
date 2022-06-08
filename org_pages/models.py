from django.db import models
from django.urls import reverse
from uuid import uuid4
from django.utils.text import slugify
import httpx
import os

def gen_upload_path():
    return f"media/logos/{uuid4()}/"

# Create your models here.
class DiversityFocus(models.Model):
    name = models.CharField(max_length=200)
    parent_diversity_focus = models.ManyToManyField('self', blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Diversity Focuses'


class TechnologyFocus(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'Technology Focuses'

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    region = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=250, blank=True, null=True)
    base_query = models.CharField(max_length=250, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=5, null=True, blank=True, unique=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=5, null=True, blank=True, unique=True)

    class Meta:
        ordering = ('name', 'region', 'country')

    def __str__(self):
        return f"{self.name}, {self.region}, {self.country}".replace('None', '').replace(', ,', ',')

    def save(self):
        response = httpx.get(
                url='https://atlas.microsoft.com/search/address/json',
                params = {
                    "query": str(self),
                    "limit": 1,
                    "subscription-key": os.environ.get('AZURE_MAPS_KEY'),
                    "api-version": "1.0"
                    },
                )
        if response.status_code == 200:
            result = response.json()['results'][0]
            self.country = result['address']['country']

            if 'Municipality' in result['entityType']:
                self.name = result['address']['municipality']
                self.region = result['address'].get('countrySubdivision', None) 
            
            self.latitude = result['position']['lat']
            self.longitude = result['position']['lon']
        return super().save()

    def get_absolute_url(self):
        return reverse('location_filter', kwargs={'pk': self.pk})


class ParentOrganization(models.Model):
    slug = models.SlugField(max_length=200, unique=True, null=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    diversity_focus = models.ManyToManyField(
        DiversityFocus, blank=True, related_name='org_diversity_focus'
        )
    featured=models.BooleanField(default=False)
    url = models.URLField(blank=True)
    social_links = models.TextField(blank=True)
    events_link = models.URLField(blank=True)
    online_only = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    technology_focus = models.ManyToManyField(
        TechnologyFocus, blank=True, related_name='org_technology_focus'
        )
    code_of_conduct = models.URLField(blank=True)
    logo = models.ImageField(upload_to=gen_upload_path(), blank=True)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('parent_org_detail', kwargs={'slug': self.slug})

    def set_children_focuses(self):
        for child in Organization.objects.filter(parent=self):
            child.description = self.description
            child.diversity_focus.set(self.diversity_focus.all())
            child.technology_focus.set(self.technology_focus.all())
            child.save()

    def save(self):
        self.slug = slugify(self.name)
        self.set_children_focuses()
        super().save()
        

class Organization(models.Model):
    slug = models.SlugField(max_length=200, unique=True, null=True)
    name = models.CharField(max_length=200, unique=True)
    code_of_conduct = models.URLField(blank=True)
    description = models.TextField(blank=True)
    diversity_focus = models.ManyToManyField(
        DiversityFocus, related_name='parent_org_diversity_focus', blank=True
        )
    url = models.URLField(blank=True, null=True)
    social_links = models.TextField(blank=True)
    events_link = models.URLField(blank=True)
    online_only = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(
        ParentOrganization, on_delete=models.CASCADE, blank=True, null=True
        )
    technology_focus = models.ManyToManyField(
        TechnologyFocus, blank=True, related_name='parent_org_technology_focus',
        )
    logo = models.ImageField(upload_to='media/logos', blank=True)

    def save(self):
        if self.parent and not self.logo:
            self.logo = self.parent.logo
        if self.parent and self.name == self.parent.name:
            self.name = f"{self.name} {self.location.name}"
        # self.slug = slugify(self.name)
        super().save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('org_detail', kwargs={'slug': self.slug})