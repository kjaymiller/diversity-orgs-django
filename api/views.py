from django.views.generic.base import TemplateView
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.views import APIView
from org_pages.models import Organization
import api.serializers as serializers
from django.db.models import Q

# Create your views here.


class AboutTemplateView(TemplateView):
    template_name = "API/about.html"


class ExampleView(APIView):
    """
    An example view.
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            "user": str(request.user),  # `django.contrib.auth.User` instance.
            "auth": str(request.auth),  # None
        }

        content["msg"] = f"Hello, {request.user.username}"

        return Response(content)


class OrgMapQuerySet(viewsets.ModelViewSet):
    """View for returning the map organization data"""

    serializer_class = serializers.OrganizationMappingSerializer

    def get_queryset(self):
        base_params = self.request.query_params.dict()
        base_params.pop("format", None)
        orgs = (
            Organization.objects.filter(**base_params)
            .filter(parent__isnull=False)
            .filter(location__isnull=False)
            .filter(location__latitude__isnull=False)
        )
        return orgs

    def list(self, *args, **kwargs):
        context = super().list(*args, **kwargs)
        return Response({"type": "FeatureCollection", "features": [x["coords"] for x in context.data]})


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    lookup_field = "name"
    serializer_class = serializers.OrganizationSerializer


class OrganizationListView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer


class LocationOrganizationListView(generics.ListAPIView):
    serializer_class = serializers.OrganizationSerializer

    def get_queryset(self):
        base_params = self.request.query_params.dict()
        orgs = Organization.objects.all()
        if city := base_params.get("city"):
            print(f"searching for {city=}")
            orgs = orgs.filter(location__name=city)
        if region := base_params.get("region"):
            orgs = orgs.filter(location__region=region)
        if country := base_params.get("country"):
            orgs = orgs.filter(location__country__icontains=country)
        return orgs


class OrganizerListView(generics.ListCreateAPIView):
    serializer_class = serializers.OrganizationSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.data.get("include_children", False):
            return Organization.objects.filter(
                Q(parent__id__in=self.request.user.organizations.values("id"))
                | Q(id__in=self.request.user.organizations.values("id")),
            )

        return self.request.user.organizations.all()


class OrganizerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for returning the organizer data"""

    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(
            Q(id__in=self.request.user.organizations.values("id"))
            | Q(parent_id__in=self.request.user.organizations.values("id")),
        )
