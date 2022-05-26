from django.urls import path
from .views import (
    HomePageView,
    LocationFilterView,
    OrgListView, 
    OrgDetailView, 
    ParentOrgDetailView,
    ParentOrgListView,
)

urlpatterns = [
    path("",HomePageView.as_view(), name="home"),
    path("orgs/",OrgListView.as_view(), name="orgs"),
    path("orgs/<int:pk>",OrgDetailView.as_view(), name="org_detail"),
    path("parent_orgs/",ParentOrgListView.as_view(), name="parent_orgs"),
    path("parent_orgs/<int:pk>",ParentOrgDetailView.as_view(), name="parent_org_detail"),
    path("filter/location/<int:region_pk>",LocationFilterView.as_view(), name="location_filter"),
]