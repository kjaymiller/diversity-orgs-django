from django.urls import path
import api.views as views


urlpatterns = [
    path("map/", views.OrgMapQuerySet.as_view({"get": "list"}), name="org_map"),
    path("organizations/<str:slug>", views.OrganizationDetailView.as_view(), name="org_detail"),
    path("parent_organizations/<str:slug>", views.ParentOrganizationDetailView.as_view(), name="parent_org_detail"),
]