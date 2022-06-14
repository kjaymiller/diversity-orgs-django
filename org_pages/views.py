from django.views.generic import ListView, DetailView
from django.conf import settings
from django.db.models import Q, Count
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from .models import (
    DiversityFocus,
    Organization, 
    Location,
)

# Create your views here.
class HomePageView(ListView):
    template_name = "home.html"
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_orgs'] = self.model.objects.filter(is_featured=True)
        context['map'] = 'parent__is_featured=True'
        context['map_sprites'] = [(x.slug, x.logo.url) for x in context['featured_orgs']]
        context['AZURE_MAPS_KEY'] = settings.AZURE_MAPS_KEY
        return context

class SearchResultsView(ListView):
    template_name = "search_results.html"
    model = Organization
    
    def get_queryset(self):

        query = self.request.GET.get('q')
    
        if name_match:=Organization.objects.filter(name__icontains=query):
            return name_match
            
        if location_match:=Organization.objects.filter(Q(location__name=query)|Q(location__region=query)|Q(location__country=query)):
            return location_match
            
        if diversity_match:=Organization.objects.filter(diversity_focus__name=query):
            return diversity_match
            
        if techonology_match:=Organization.objects.filter(technology_focus__name=query):
            return techonology_match
            
        # Create vectors for search
        query = SearchQuery(self.request.GET.get('q'), search_type='websearch')
        vector = SearchVector('diversity_focus__name', weight='C') \
                + SearchVector('technology_focus__name', weight='B') \
                + SearchVector('location__name', weight='C') \
                + SearchVector('location__region', weight='C') \
                + SearchVector('location__country', weight='B') \
            
        queryset = Organization.objects.annotate(
                rank=SearchRank(vector, query, weights=[0.1, 0.3, 0.6, 1.0]),
                ).filter(rank__gte=0.55).order_by('-rank')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        context['parents'] = self.object_list.values('parent__name').distinct()
        print(context['parents'])
        return context

class OrgListView(ListView):
    template_name = 'org_list.html'
    model = Organization

class OrgDetailView(DetailView):
    template_name = 'org_detail.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if children:= self.model.objects.filter(parent=self.object).exclude(location=None):
            context['children'] = children.order_by('location__country', 'location__name')
            context['map'] = f'parent={self.object.pk}'
            context['map_sprites'] = [(self.object.slug, self.object.logo.url)]
            context['AZURE_MAPS_KEY'] = settings.AZURE_MAPS_KEY
        
        else:
            diversity_focuses = []

            for focus in self.object.diversity_focus.all():
                if focus.parents:
                    for parent in focus.parents.all():
                        diversity_focuses.append(parent)
            
            diversity_focuses.extend(self.object.diversity_focus.all())
            technology_focuses = []
            for focus in self.object.technology_focus.all():
                if focus.parents:
                    for parent in focus.parents.all():
                        technology_focuses.append(parent)
            technology_focuses.extend(self.object.technology_focus.all())
            
            other_orgs = self.model.objects.filter(location=self.object.location,
            ).exclude(pk=self.object.pk)

            if diversity_focuses:
                other_orgs = other_orgs.filter(diversity_focus__in=diversity_focuses)

            if technology_focuses:
                other_orgs = other_orgs.filter(technology_focus__in=technology_focuses)
            context['other_orgs'] = other_orgs
        return context

class LocationFilterView(ListView):
    template_name = 'location_filter.html'
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(location__pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = Location.objects.get(pk=self.kwargs['pk'])
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
        context['location'] = Location.objects.get(pk=self.kwargs['location__pk'])
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