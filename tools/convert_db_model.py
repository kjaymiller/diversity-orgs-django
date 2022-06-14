import json
from org_pages.models import Organization, Location, TechnologyFocus, DiversityFocus
from django.db import models

with open('tools/diversity-orgs.json', 'r') as f:
    data = json.load(f)

def create_or_add(model:models.Model, key_value:str) -> models.Model:
    
    if model_obj:=model.objects.filter(name=key_value):
        return model_obj[0]

    else:
        obj = model(name=key_value)
        obj.save()
        return obj

for org in data:
    if 'name' not in org or Organization.objects.filter(name=org['name']):
       continue

    technology_focus = [create_or_add(TechnologyFocus, focus) for focus in org.get('technology_focus', [])]
    diversity_focus = [create_or_add(DiversityFocus, focus) for focus in org.get('diversity_focus', [])]
    
    obj = Organization(
        name=org.get('name'),
        url = org.get('url'),
    )
    
    obj.save()
    
    obj.technology_focus.set(technology_focus)
    obj.diversity_focus.set(diversity_focus)
    obj.save()

    if parent_org:=org.get('parent_organization'):
        obj.parent = create_or_add(Organization, parent_org)
        obj.save()

        if base_location:=org.get('location'):
            if base_location['name'].lower() == 'online':
                obj.online_only = True
                
            elif loc := Location.objects.filter(base_query=base_location['base_query']):
                obj.location = loc[0]
                
            else:
                lat, lon = base_location['location'][1], base_location['location'][0]
                location = Location(
                        name=base_location['name'],
                        country=base_location.get('country',''),
                        region=base_location.get('region',''),
                        base_query=org['location'].get('base_query', None),
                        latitude=lat,
                        longitude=lon,
                    )

            obj.save()