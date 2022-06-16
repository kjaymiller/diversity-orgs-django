from django.urls import path
import api.views as views


urlpatterns = (
    path("", views.ExampleView.as_view(), name="info"),
    path("locations", views.LocationOrganizationListView.as_view(), name="org_by_location"),
    path("map/", views.OrgMapQuerySet.as_view({"get": "list"}), name="org_map"),
    path("my/organization/<int:pk>", views.OrganizerDetailView.as_view(), name="my_org"),
    path("my/organizations/", views.OrganizerListView.as_view(), name="my_orgs"),
    path("organizations/", views.OrganizationDetailView.as_view(), name="org_detail"),
)   