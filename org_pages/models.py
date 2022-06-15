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
    parents = models.ManyToManyField('self', blank=True, symmetrical=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Diversity Focuses'


class TechnologyFocus(models.Model):
    name = models.CharField(max_length=200)
    parents = models.ManyToManyField('self', blank=True, symmetrical=False)


    class Meta:
        ordering = ['name']
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
        ordering = ('country', 'region', 'name')

    def __str__(self):
        return f"{self.name}, {self.region}, {self.country}".replace('None', '').replace(', ,', ',')

    def save(self):
        if not self.latitude:
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
                    self.region = result['address'].get('countrySubdivisionName', result['address'].get('countrySubdivison', '')) 
                
                self.latitude = result['position']['lat']
                self.longitude = result['position']['lon']
        return super().save()

    def get_absolute_url(self):
        return reverse('location_filter', kwargs={'pk': self.pk})


class Organization(models.Model):
    slug = models.SlugField(max_length=200, unique=True, null=True)
    name = models.CharField(max_length=200, unique=True)
    code_of_conduct = models.URLField(blank=True)
    description = models.TextField(blank=True)
    diversity_focus = models.ManyToManyField(
        DiversityFocus, related_name='parent_org_diversity_focus', blank=True
        )
    is_featured = models.BooleanField(default=False)
    url = models.URLField(blank=True, null=True)
    social_links = models.TextField(blank=True)
    events_link = models.URLField(blank=True)
    online_only = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True
        )
    technology_focus = models.ManyToManyField(
        TechnologyFocus, blank=True, related_name='parent_org_technology_focus',
        )
    logo = models.ImageField(upload_to='media/logos', blank=True)

    class Meta:
        ordering = ('parent__exact', 'name',)

    def save(self):
        super().save()

    def get_from_parents(self):
        if self.parent:
            if not self.logo:
             self.logo = self.parent.logo
        
            if self.name == self.parent.name:
                self.name = f"{self.name} {self.location.name}"

            if not self.description:
                self.description = self.parent.description

            if not self.code_of_conduct:
                self.code_of_conduct = self.parent.code_of_conduct

            if not self.diversity_focus.all():
                self.diversity_focus.set(self.parent.diversity_focus.all())
                
            if not self.technology_focus.all():
                self.technology_focus.set(self.parent.technology_focus.all())
                
        if not self.slug:    
            self.slug = slugify(self.name)
        
        return super().save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('org_detail', kwargs={'slug': self.slug})

    def set_children_focuses(self):
        for obj in Organization.objects.filter(parent=self):
            obj.description = self.description
            obj.diversity_focus.set(self.diversity_focus.all())
            obj.technology_focus.set(self.technology_focus.all())
            if not obj.logo:
                obj.logo = self.logo
            obj.save()
    