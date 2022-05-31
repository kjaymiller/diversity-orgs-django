from django.db import models
from django.urls import reverse


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
    name = models.CharField(max_length=200)
    region = models.CharField(max_length=250, blank=True)
    country = models.CharField(max_length=250, blank=True)
    base_query = models.CharField(max_length=250, blank=True)
  
    class Meta:
        ordering = ('pk', 'name', 'region', 'country')

    def __str__(self):
        return f"{self.name}, {self.region}, {self.country}"

    def get_absolute_url(self):
        return reverse('filter_location', kwrgs={'pk': self.pk})


class ParentOrganization(models.Model):
    name = models.CharField(max_length=200)
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
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('org_detail', kwrgs={'pk': self.pk})

    def set_children_focuses(self):
        for child in Organization.objects.filter(parent=self):
            child.description = self.description
            child.diversity_focus.set(self.diversity_focus.all())
            child.technology_focus.set(self.technology_focus.all())
            child.save()

    def save(self):
        self.set_children_focuses()
        super().save()


class Organization(models.Model):
    name = models.CharField(max_length=200)
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
    

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('org_detail', kwrgs={'pk': self.pk})