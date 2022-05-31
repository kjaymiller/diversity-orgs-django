from django.views.generic import ListView, DetailView
from django.urls import reverse
from .models import (
    DiversityFocus,
    Organization, 
    ParentOrganization,
    Location,
    TechnologyFocus,
)
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank

# Create your views here.
class HomePageView(ListView):
    template_name = "home.html"
    model = ParentOrganization
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_orgs'] = ParentOrganization.objects.filter(featured=True)
        return context

class SearchResultsView(ListView):
    template_name = "search_results.html"
    model = Organization
    
    def get_queryset(self):

        query = self.request.GET.get('q')

        if location_match:=Organization.objects.filter(Q(location__name=query)|Q(location__region=query)|Q(location__country=query)):
            return location_match
            
        elif diversity_match:=Organization.objects.filter(diversity_focus__name=query):
            return diversity_match
            
        elif techonology_match:=Organization.objects.filter(technology_focus__name=query):
            return techonology_match
            
        # Create vectors for search
        else:
            query = SearchQuery(self.request.GET.get('q'), search_type='websearch')
            vector = SearchVector('diversity_focus__name', weight='C') \
                + SearchVector('name', weight='D') \
                + SearchVector('technology_focus__name', weight='B') \
                + SearchVector('location__name', weight='C') \
                + SearchVector('location__region', weight='C') \
                + SearchVector('location__country', weight='B') \
            
            queryset = Organization.objects.annotate(
                rank=SearchRank(vector, query, weights=[0.1, 0.3, 0.6, 1.0]),
                ).filter(rank__gte=0.5).order_by('-rank')
            
            print([(entry, entry.rank) for entry in queryset])
            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context
    


class OrgListView(ListView):
    template_name = 'org_list.html'
    model = Organization

class OrgDetailView(DetailView):
    template_name = 'org_detail.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['others'] = Organization.objects.filter(
                location__region = context['organization'].location.region
                ).exclude(
                    location__region = None).exclude(
                    name=context['organization'].name)
        return context

class ParentOrgListView(ListView):
    template_name = 'parent_org_list.html'
    model = ParentOrganization

class ParentOrgDetailView(DetailView):
    template_name = 'parent_org_detail.html'
    model = ParentOrganization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        children = Organization.objects.filter(parent=context['parentorganization'])
        context['organization_list'] = children.order_by('name')
        return context

class LocationFilterView(ListView):
    template_name = 'location_filter.html'
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(location__pk=self.kwargs['region_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = Location.objects.get(pk=self.kwargs['region_pk'])
        return context


class DiversityFocusFilterView(ListView):
    template_name = 'location_filter.html'
    model = Organization

    def get_queryset(self):
        return Organization.objects \
            .filter(location__pk=self.kwargs['region_pk']) \
            .filter(diversity_focus=self.kwargs['diversity'])


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diversity'] = DiversityFocus.objects.get(pk=self.kwargs['diversity'])
        context['location'] = Location.objects.get(pk=self.kwargs['region_pk'])
        return context

class TechnologyFocusFilterView(ListView):
    template_name = 'location_filter.html'
    model = Organization

    def get_queryset(self):
        return Organization.objects \
            .filter(location__pk=self.kwargs['region_pk']) \
            .filter(diversity_focus=self.kwargs['technology'])


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['technology'] = DiversityFocus.objects.get(pk=self.kwargs['technology'])
        context['location'] = Location.objects.get(pk=self.kwargs['region_pk'])
        return context

class OnlineDiversityFocusFilterView(ListView):
    template_name = 'location_filter.html'
    model = Organization

    def get_queryset(self):
        return Organization.objects \
            .filter(online_only=True) \
            .filter(diversity_focus=self.kwargs['diversity'])


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diversity'] = DiversityFocus.objects.get(pk=self.kwargs['diversity'])
        context["location"] = "Online"
        return context

class OnlineTechnologyFocusFilterView(ListView):
    template_name = 'location_filter.html'
    model = Organization

    def get_queryset(self):
        return Organization.objects \
            .filter(location__pk=self.kwargs['region_pk']) \
            .filter(diversity_focus=self.kwargs['technology'])


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['technology'] = DiversityFocus.objects.get(pk=self.kwargs['technology'])
        context["location"] = "Online"
        return context