import json
from org_pages.models import Organization, ParentOrganization, Location, TechnologyFocus, DiversityFocus
from django.db import models
from django.contrib.gis.geos import Point


with open('diversity-orgs.json', 'r') as f:
    data = json.load(f)

def create_or_add(model:models.Model, key_value:str) -> models.Model:
    if model_obj:=model.objects.filter(name=key_value):
        return model_obj[0]
    else:
        return model.objects.create(name=key_value)


for org in data:
    if 'name' not in org:
       continue
    technology_focus = [create_or_add(TechnologyFocus, focus) for focus in org.get('technology_focus', [])]
    diversity_focus = [create_or_add(DiversityFocus, focus) for focus in org.get('diversity_focus', [])]
    social_links = ','.join(org.get('links', []))

    if parent_org:=org.get('parent_organization'):
       parent = create_or_add(ParentOrganization, parent_org)
    else:
        parent = None

    if base_location:=org.get('location'):
        if base_location['name'].lower() == 'online':
            online_only = True
        else:
            if  loc_object:= Location.objects.filter(
                    name=base_location.get('name', ''),
                    region=base_location.get('region', '')):
                location = loc_object[0]

            elif coords:=base_location.get('location'):
                lon, lat = [float(x) for x in coords.split(', ')]
                location = Location.objects.create(
                    name=base_location['name'],
                    country=base_location.get('country',''),
                    location=Point(lat, lon),
                    region=base_location.get('region',''),
                    base_query=org['location'].get('base_query', None),
                )

    kwargs = {
        'social_links': social_links,
        'name': org['name'],
        'location': location,
        'url': org.get('url', None),
        'parent': parent,
    }

    obj = Organization(**kwargs)
    obj.save()
    obj.technology_focus.set(technology_focus)
    obj.diversity_focus.set(diversity_focus)
    obj.save()
    
