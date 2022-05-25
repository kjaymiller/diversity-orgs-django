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
    ParentOrganization,
    Organization,
    TechnologyFocus,
    DiversityFocus,
    Location,
    )

for registry in registries:
    admin.site.register(registry)
