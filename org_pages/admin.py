from django.contrib import admin

# Register your models here.

from .models import (
    Organization,
    TechnologyFocus,
    DiversityFocus,
    Location,
)

registries = (
    TechnologyFocus,
    DiversityFocus,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "location")
    list_filter = ("location__country",)
    search_fields = ("name", "parent__name", "location__name")
    autocomplete_fields = ("parent", "location")
    prepopulated_fields = {"slug": ("name",)}



@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_filter = ("country",)
    list_display = ("name", "region", "country")
    search_fields = ("name", "region", "country")


for registry in registries:
    admin.site.register(registry)
