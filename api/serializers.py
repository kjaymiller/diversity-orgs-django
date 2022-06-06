from rest_framework.request import Request
from django.http import HttpRequest
from org_pages.models import Organization, ParentOrganization, Location
from rest_framework import serializers

class OrganizationMappingSerializer(serializers.ModelSerializer):
    coords = serializers.SerializerMethodField()
    class Meta:
        model = Organization
        fields = ('coords',)

    def get_coords(self, obj):
        if obj.location:
            if latitude:=obj.location.latitude:
                 if longitude:=obj.location.longitude:
                    return {
                        "type": "Feature",
                        "properties": {"parent_name": obj.parent.name},
                        "geometry": {
                            "type": "Point",
                            "coordinates": [obj.location.longitude, obj.location.latitude]
                        },
                    }
        return None

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        depth = 1

class LimitedOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    location = serializers.StringRelatedField()

    class Meta:
        model = Organization
        fields = ('name', 'location', 'url')
        depth = 1
       

class ParentOrganizationSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ParentOrganization
        fields = '__all__'

    def get_children(self, obj):
        return LimitedOrganizationSerializer(Organization.objects.filter(parent=obj), many=True).data