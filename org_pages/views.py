from django.http import Http404
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from .models import (
    DiversityFocus,
    Organization,
    Location,
    TechnologyFocus,
)
from .forms import OrgForm, CreateOrgForm

def is_organizer(user, org):
    """Check if a user is authenticated and an organizer of an organization."""
    if not user.is_authenticated:
        return False

    if org.parent and user in org.parent.organizers.all():
        return True

    if user in org.organizers.all():
        return True

    if user.is_superuser:
        return True
    
    return False


# Create your views here.
class HomePageView(ListView):
    template_name = "home.html"
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_orgs"] = self.model.objects.filter(is_featured=True)
        context["map"] = "is_featured=True"
        context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY
        return context


class SearchResultsView(ListView):
    template_name = "search_results.html"
    model = Organization

    def get_queryset(self):

        query = self.request.GET.get("q")

        if name_match := Organization.objects.filter(name__iexact=query):
            return name_match

        if name_match := Organization.objects.filter(name__icontains=query):
            return name_match

        if location_match := Organization.objects.filter(
            Q(location__name=query) | Q(location__region=query) | Q(location__country=query)
        ):
            return location_match

        if diversity_match := Organization.objects.filter(diversity_focus__name=query):
            return diversity_match

        if techonology_match := Organization.objects.filter(technology_focus__name=query):
            return techonology_match

        # Create vectors for search
        query = SearchQuery(self.request.GET.get("q"), search_type="websearch")
        vector = (
            SearchVector("diversity_focus__name", weight="B")
            + SearchVector("technology_focus__name", weight="B")
            + SearchVector("location__name", weight="C")
            + SearchVector("location__region", weight="C")
            + SearchVector("location__country", weight="C")
        )
        queryset = (
            Organization.objects.annotate(
                rank=SearchRank(vector, query, weights=[0.1, 0.3, 0.6, 1.0]),
            )
            .filter(rank__gte=0.4)
            .order_by("-rank")
            .distinct()
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        context["parents"] = self.object_list.values("parent__name").distinct()
        print(context["parents"])
        return context


class OrgListView(ListView):
    template_name = "org_list.html"
    model = Organization


class OrgDetailView(DetailView):
    template_name = "orgs/detail.html"
    model = Organization
    form_class = CreateOrgForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_organizer'] = is_organizer(self.request.user, self.object) or self.request.user.is_superuser

        if children := self.model.objects.filter(parent=self.object):
            context["children"] = children.order_by("location__country", "location__name")
            context["map"] = f"parent={self.object.pk}"
            context["map_sprites"] = [(self.object.slug, self.object.logo.url)]
            context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY
            
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

            other_orgs = self.model.objects.filter(
                location=self.object.location,
            ).exclude(pk=self.object.pk)

            if diversity_focuses:
                other_orgs = other_orgs.filter(diversity_focus__in=diversity_focuses)

            if technology_focuses:
                other_orgs = other_orgs.filter(technology_focus__in=technology_focuses)
            context["other_orgs"] = other_orgs.distinct()
        return context


class CreateOrgView(LoginRequiredMixin, CreateView):
    template_name = "orgs/create.html"
    model = Organization
    form_class = CreateOrgForm
    
    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self, request):
        super().post()
        self.object.organizers.add(self.request.user)
        self.object.save()
        return redirect(self.get_success_url())



class UpdateOrgView(LoginRequiredMixin, UpdateView):
    """update form if organization is in organization"""
    template_name = "orgs/update.html"
    model = Organization
    form_class = OrgForm

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        initial["diversity_focus"] = (", ").join([x.name for x in self.object.diversity_focus.all()])
        initial["technology_focus"] = (", ").join([x.name for x in self.object.technology_focus.all()])
        initial["organizers"] = (", ").join([x.email for x in self.object.organizers.all()])
        if self.object.location:
            location_fields = (
                self.object.location.name,
                self.object.location.region,
                self.object.location.country,
            )
            initial['location'] = ", ".join([x for x in location_fields if x])
        if self.object.parent:
            initial['parent'] = self.object.parent.name
    
        return initial

        
    def dispatch(self, request, *args, **kwargs):
        """Raise a 404 if user is not an organizer."""
        if  is_organizer(request.user, self.get_object()):
            return super().dispatch(request, *args, **kwargs)
        raise Http404("You must be an organization member to update an organization.")
        

class ClaimOrgView(LoginRequiredMixin, UpdateView):
    """Claim an organization if there are no organizers. This request must be reviewed."""
    template_name = "orgs/update.html"
    model = Organization
    form_class = OrgForm

class LocationFilterView(ListView):
    template_name = "location_filter.html"
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(location__pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = Location.objects.get(pk=self.kwargs["pk"])
        return context


class DiversityFocusFilterView(ListView):
    template_name = "location_filter.html"
    model = Organization
    paginate_by=20

    def get_queryset(self):
        diversity=DiversityFocus.objects.get(name__iexact=self.kwargs["diversity"])
        queryset = Organization.objects.filter(diversity_focus=diversity)
        if location:=self.request.GET.get('location', None):
            return queryset.filter(location__pk=location) # Disconnect and filter by location

        # The other checks are additive
        if city:=self.request.GET.get('city', None):
            queryset = queryset.filter(location__name=city)
        if region:=self.request.GET.get('region', None):
            queryset = queryset.filter(location__region=region)
        if country:=self.request.GET.get('country', None):
            queryset = queryset.filter(location__country=country)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["diversity"] = diversity=DiversityFocus.objects.get(name__iexact=self.kwargs["diversity"])
        if location:=self.request.GET.get('location', None):
            context["location"] = Location.objects.get(pk=location)
        
        return context


class TechnologyFocusFilterView(ListView):
    template_name = "location_filter.html"
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(location__pk=self.kwargs["region_pk"]).filter(
            diversity_focus=self.kwargs["technology"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["technology"] = TechnologyFocus.objects.get(pk=self.kwargs["technology"])
        context["location"] = Location.objects.get(pk=self.kwargs["region_pk"])
        return context


class OnlineDiversityFocusFilterView(ListView):
    template_name = "location_filter.html"
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(online_only=True).filter(diversity_focus=self.kwargs["diversity"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["diversity"] = DiversityFocus.objects.get(pk=self.kwargs["diversity"])
        context["location"] = "Online"
        return context


class OnlineTechnologyFocusFilterView(ListView):
    template_name = "location_filter.html"
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(location__pk=self.kwargs["region_pk"]).filter(
            diversity_focus=self.kwargs["technology"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["technology"] = DiversityFocus.objects.get(pk=self.kwargs["technology"])
        context["location"] = "Online"
        return context
