from org_pages.models import Organization
from rest_framework import serializers


class OrganizationMappingSerializer(serializers.ModelSerializer):
    coords = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("coords",)

    def get_coords(self, obj):
        if obj.location:
            if obj.location.latitude and obj.location.longitude:
                return {
                    "type": "Feature",
                    "properties": {
                        "url": obj.get_absolute_url(),
                        "name": obj.name,
                    },
                    "geometry": {"type": "Point", "coordinates": [obj.location.longitude, obj.location.latitude]},
                }
        return None


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        exclude = ("logo", "organizers")
        extra_kwargs = {"name": {"required": False}}
        depth = 1


class LimitedOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    location = serializers.StringRelatedField()

    class Meta:
        model = Organization
        fields = ("name", "location", "url")
        depth = 1
