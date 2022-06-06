from django.urls import path
import api.views as views


urlpatterns = [
    path("featured", views.FeaturedOrganizations.as_view({'get': 'list'}), name="featured_orgs"),
    path("organizations/<int:pk>", views.OrganizationDetailView.as_view(), name="org_detail"),
    path("parent_organizations/<str:name>", views.ParentOrganizationDetailView.as_view(), name="parent_org_detail"),
]