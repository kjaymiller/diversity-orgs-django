from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, generics
from org_pages.models import Organization, ParentOrganization
import api.serializers as serializers
# Create your views here.

class FeaturedOrganizations(viewsets.ModelViewSet):
    queryset = Organization.objects \
        .filter(parent__featured=True) \
        .filter(location__isnull=False) \
        .filter(location__latitude__isnull=False)
    serializer_class = serializers.OrganizationMappingSerializer

    def list(self, *args, **kwargs):
        context = super().list(*args, **kwargs)
        return Response({
                "type": "FeatureCollection",
                "features": [x['coords'] for x in context.data]
                })

class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    lookup_field = 'name'
    serializer_class = serializers.OrganizationSerializer

class ParentOrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParentOrganization.objects.all()
    lookup_field = 'name'
    serializer_class = serializers.ParentOrganizationSerializer