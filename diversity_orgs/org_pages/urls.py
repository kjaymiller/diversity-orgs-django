from django.urls import path
from .views import OrgPageView, ParentOrgPageView

urlpatterns = [
    path("",OrgPageView.as_view(), name="home"),
    path("parent_orgs/",ParentOrgPageView.as_view(), name="parent_orgs"),
]