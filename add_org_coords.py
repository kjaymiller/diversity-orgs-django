# Get the coordinates of each location object

from org_pages.models import Location
import os
import httpx

def get_location_query(location:Location) -> dict[str]:
    return {"query": f"?query={location}&limit=1"}

locations = {
        "batchItems": [get_location_query(loc) for loc in Location.objects.all()]
    }

subscription_key = os.environ.get('AZURE_MAPS_KEY')
# To get create a new request
url = f"https://atlas.microsoft.com/search/address/batch/json?&api-version=1.0&subscription-key={subscription_key}"
# print(url)
initial_request = httpx.post(url, json=locations)

request = httpx.get(initial_request.headers['location'])

if request.status_code in [200, 202]:
    data = request.json()['batchItems']
    for loc in data:
        if loc['statusCode'] == 200:
            result = loc['response']['results'][0]
            
            location = Location.objects.filter(name=result['address'].get(
                'municipality', None), country=result['address'].get('country', None)).update(
                    name = result['address'].get('municipality', None),
                    region = result['address'].get('countrySubdivisionName', result['address'].get('countrySubdivision', None)),
                    country = result['address'].get('country', None),
                    latitude = result['position']['lat'],
                    longitude = result['position']['lon'],
                )
        
else:
    print(request.status_code)