from tokenize import Token
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.views import APIView
from org_pages.models import Organization
import api.serializers as serializers
# Create your views here.

class ExampleView(APIView):
    """
    An example view.
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth), # None
        }

        content['msg'] = f"Hello, {request.user.username}"

        return Response(content)

class OrgMapQuerySet(viewsets.ModelViewSet):
    """View for returning the map organization data"""
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


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    lookup_field = 'name'
    serializer_class = serializers.OrganizationSerializer


class OrganizationListView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer

class OrganizerListView(generics.ListCreateAPIView):
    serializer_class = serializers.OrganizationSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.organizations.all()
        
class OrganizerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for returning the organizer data"""
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrganizationSerializer

    def get_queryset(self):
        return self.request.user.organizations.all()