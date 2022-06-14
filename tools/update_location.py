from org_pages.models import Location, Organization

def set_location(location: str):
    """Update the location of the organization"""
    location_obj = Location.objects.get(name=location)
    return Organization.objects.filter(name__icontains=location).update(location=location_obj)


set_location("Seattle")