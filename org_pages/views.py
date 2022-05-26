from multiprocessing import parent_process
from django.views.generic import ListView, DetailView
from .models import Organization, ParentOrganization, Location
from django.contrib.postgres.search import SearchVector, SearchQuery

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
        queryset = Organization.objects.annotate(
            search=SearchVector(
                'name', 'diversity_focus', 'technology_focus', 'parent__name', 'location__name', 'location__region', 'location__country',
                )
            ).filter(search=SearchQuery(self.request.GET.get('q'), search_type="websearch"))
        return queryset.distinct('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        print(context)
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