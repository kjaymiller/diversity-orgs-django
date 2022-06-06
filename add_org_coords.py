# Get the coordinates of each location object

from org_pages.models import Location
import os
import httpx
import json
def get_location_query(location:Location) -> dict[str]:
    return {"query": f"?query={location}&limit=1"}

locations = {
        "batchItems": [get_location_query(loc) for loc in Location.objects.all()]
    }

subscription_key = os.environ.get('AZURE_MAPS_KEY')
# To get create a new request
# url = f"https://atlas.microsoft.com/search/address/batch/json?&api-version=1.0&subscription-key={subscription_key}"
# print(url)
# request = httpx.post(url, json=locations)

url = f"https://atlas.microsoft.com/search/address/batch/4113de05-758b-416f-8c44-9b0f74c60906?subscription-key={subscription_key}&api-version=1.0"
request = httpx.get(url)

if request.status_code in [200, 202]:
    data = request.json()['batchItems']
    for loc in data:
        print(loc)
        if loc['statusCode'] == 200:
            result = loc['response']['results'][0]
            if result.get('entityType', '') != 'Municipality':
                print(result)
                continue
            location = Location.objects.filter(name=result['address']['municipality']).filter(country=result['address']['country'])

            if location:
                entry = location[0]
                entry.latitude=result['position']['lat']
                entry.longitude=result['position']['lon']
                entry.save()
        
else:
    print(request.status_code, request.text)