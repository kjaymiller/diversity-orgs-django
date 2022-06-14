import org_pages.models as org_models
from django.utils.text import slugify

for org in org_models.Organization.objects.all():
    org_list = org_models.Organization.objects.filter(name=org.name)
    if len(org_list) > 1:
        for org in org_list:
            org.name = f"{org.name} {org.location.name}"
    org.slug = slugify(org.name)
    org.save()


for orgs in (org_models.Organization):
    for org in orgs.objects.filter(slug__isnull=True):
        org.slug = slugify(org.name)
        org.save()