from django.contrib import admin

# Register your models here.

from .models import ParentOrganization, Organization

registries = (
    ParentOrganization,
    Organization,
    )

for registry in registries:
    admin.site.register(registry)
