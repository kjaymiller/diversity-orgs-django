from django.urls import path
import api.views as views


urlpatterns = [
    path("", views.ExampleView.as_view(), name="index"),
    path("map/", views.OrgMapQuerySet.as_view({"get": "list"}), name="org_map"),
    path("organizations/<str:slug>", views.OrganizationDetailView.as_view(), name="org_detail"),
]