from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, generics
from org_pages.models import Organization, ParentOrganization
import api.serializers as serializers
# Create your views here.


class OrgMapQuerySet(viewsets.ModelViewSet):
    serializer_class = serializers.OrganizationMappingSerializer

    def get_queryset(self):
        base_params = self.request.query_params.dict()
        base_params.pop('format', None)
        orgs = Organization.objects.filter(**base_params) \
        .filter(parent__isnull=False) \
        .filter(location__isnull=False) \
        .filter(location__latitude__isnull=False)
        return orgs

    def list(self, *args, **kwargs):
        context = super().list(*args, **kwargs)
        return Response({
                "type": "FeatureCollection",
                "features": [x['coords'] for x in context.data]
                })


class FeaturedOrganizations(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects \
        .filter(parent__featured=True) \
        
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