from django.urls import path
import org_pages.views as views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("search/", views.SearchResultsView.as_view(), name="search"),
    path("orgs/create", views.CreateOrgView.as_view(), name="create_org"),
    path("orgs/<slug:slug>", views.OrgDetailView.as_view(), name="org_detail"),
    path("orgs/<slug:slug>/update", views.UpdateOrgView.as_view(), name="update_org"),
    path("filter/location/<int:pk>", views.LocationFilterView.as_view(), name="location_filter"),
    path(
        "filter/location/<int:region_pk>/diversity/<str:diversity>",
        views.DiversityFocusFilterView.as_view(),
        name="diversity_filter",
    ),
    path(
        "filter/location/<int:region_pk>/technology/<str:technology>",
        views.TechnologyFocusFilterView.as_view(),
        name="technology_filter",
    ),
    path(
        "filter/online/diversity/<str:diversity>",
        views.OnlineDiversityFocusFilterView.as_view(),
        name="online_diversity_filter",
    ),
    path(
        "filter/online/technology/<str:technology>",
        views.OnlineTechnologyFocusFilterView.as_view(),
        name="online_technology_filter",
    ),
]
