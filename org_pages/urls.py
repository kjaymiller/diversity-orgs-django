from django.urls import path
import org_pages.views as views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("search/", views.SearchResultsView.as_view(), name="search"),
    path("orgs/create", views.CreateOrgView.as_view(), name="create_org"),
    path("orgs/<int:pk>/claim", views.ClaimOrgView.as_view(), name="claim_org"),
    path("orgs/<slug:slug>/suggestedit", views.SuggestEditView.as_view(), name="suggest_edit"),
    path("orgs/<slug:slug>", views.OrgDetailView.as_view(), name="org_detail"),
    path("orgs/<slug:slug>/update", views.UpdateOrgView.as_view(), name="update_org"),
    path("filter/location/<int:pk>", views.LocationFilterView.as_view(), name="location_filter"),
    path(
        "filter/diversity/<str:diversity>",
        views.DiversityFocusFilterView.as_view(),
        name="diversity_filter",
    ),
    path(
        "filter/technology/<str:technology>",
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
    path('orgs/<slug:slug>/violationreport', views.ReportViolationView.as_view(), name="violation_report"),
    path('tags/technology', views.TechnologyFocusView.as_view(), name="technology"),
    path('tags/diversity', views.DiversityFocusView.as_view(), name="diversity"),
]
