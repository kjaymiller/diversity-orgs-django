from django.urls import path
from .views import (
    HomePageView,
    LocationFilterView,
    OrgListView, 
    OrgDetailView,
    ParentOrgDetailView,
    ParentOrgListView,
    SearchResultsView,
    DiversityFocusFilterView,
    TechnologyFocusFilterView,
    OnlineDiversityFocusFilterView,
    OnlineTechnologyFocusFilterView,
)

urlpatterns = [
    path("",HomePageView.as_view(), name="home"),
    path("search/", SearchResultsView.as_view(), name="search"),
    path("parent_orgs/<slug:slug>",ParentOrgDetailView.as_view(), name="parent_org_detail"),
    path("parent_orgs/",ParentOrgListView.as_view(), name="parent_orgs"),
    path("orgs/",OrgListView.as_view(), name="orgs"),
    path("orgs/<slug:slug>",OrgDetailView.as_view(), name="org_detail"),
    path("filter/location/<int:pk>",LocationFilterView.as_view(), name="location_filter"),
    path("filter/location/<int:region_pk>/diversity/<str:diversity>",DiversityFocusFilterView.as_view(), name="diversity_filter"),
    path("filter/location/<int:region_pk>/technology/<str:technology>",TechnologyFocusFilterView.as_view(), name="technology_filter"),
    path("filter/online/diversity/<str:diversity>",OnlineDiversityFocusFilterView.as_view(), name="online_diversity_filter"),
    path("filter/online/technology/<str:technology>",OnlineTechnologyFocusFilterView.as_view(), name="online_technology_filter"),
]