from django.urls import path
from .views import (
    HomePageView,
    OrgListView, 
    OrgDetailView, 
    ParentOrgDetailView,
    ParentOrgListView,
)

urlpatterns = [
    path("",HomePageView.as_view(), name="home"),
    path("orgs/",OrgListView.as_view(), name="orgs"),
    path("orgs/<int:pk>",OrgDetailView.as_view(), name="orgs"),
    path("parent_orgs/",ParentOrgListView.as_view(), name="parent_orgs"),
    path("parent_orgs/<int:pk>/",ParentOrgDetailView.as_view(), name="parent_org_detail"),
]