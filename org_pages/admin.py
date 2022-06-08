from django.contrib import admin

# Register your models here.

from .models import (
    ParentOrganization,
    Organization,
    TechnologyFocus,
    DiversityFocus,
    Location,
)

registries = (
    TechnologyFocus,
    DiversityFocus,
    )

@admin.register(ParentOrganization)
class ParentOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('parent', 'location__country')
    search_fields = ('name', 'parent__name', 'location__name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'location')
    list_filter = ('parent', 'location__country')
    search_fields = ('name', 'parent__name', 'location__name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_filter = ('country',)
    list_display = ('name', 'region', 'country')
    search_fields = ('location__name',)


for registry in registries:
    admin.site.register(registry)
