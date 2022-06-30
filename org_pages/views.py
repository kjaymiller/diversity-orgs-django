from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Q, Count
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from .models import (
    DiversityFocus,
    Organization,
    Location,
    TechnologyFocus,
    SuggestedEdit,
    ViolationReport,
)
from .forms import (
    OrgForm,
    CreateOrgForm,
    SuggestEditForm,
    ViolationReportForm,
)

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
        aggs = context['featured_orgs'].exclude(parent=None).values('parent__name', 'parent__slug').distinct().order_by()
        context['aggs'] = [Organization.objects.get(name=agg['parent__name']) for agg in aggs]
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

        if diversity_match := Organization.objects.filter(diversity__name=query):
            return diversity_match

        if techonology_match := Organization.objects.filter(technology__name=query):
            return techonology_match

        # Create vectors for search
        query = SearchQuery(self.request.GET.get("q"), search_type="websearch")
        vector = (
            SearchVector("diversity__name", weight="B")
            + SearchVector("technology__name", weight="B")
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
            context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY
            
        else:
            diversities = []

            for focus in self.object.diversity.all():
                if focus.parents:
                    for parent in focus.parents.all():
                        diversities.append(parent)

            diversities.extend(self.object.diversity.all())
            technologies = []
            for focus in self.object.technology.all():
                if focus.parents:
                    for parent in focus.parents.all():
                        technologies.append(parent)
            technologies.extend(self.object.technology.all())

            other_orgs = self.model.objects.filter(
                location=self.object.location,
            ).exclude(pk=self.object.pk)

            if diversities:
                other_orgs = other_orgs.filter(diversity__in=diversities)

            if technologies:
                other_orgs = other_orgs.filter(technology__in=technologies)
            context["other_orgs"] = other_orgs.distinct()
        return context


class CreateOrgView(LoginRequiredMixin, CreateView):
    template_name = "orgs/create.html"
    model = Organization
    form_class = CreateOrgForm
    
    def get_success_url(self):
        return self.object.get_absolute_url()

    def post(self):
        super().post()
        self.object.organizers.add(self.request.user)
        self.object.save()
        return redirect(self.get_success_url())


class SuggestEditView(UpdateView):
    """Form that allows users to suggest edits to an organization page."""
    template_name = "orgs/update.html" # TODO:Create Custom Template
    form_class = SuggestEditForm
    model = Organization

    def get_success_url(self):
        return self.object.get_absolute_url()
    
    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        initial["diversity"] = (", ").join([x.name for x in self.object.diversity.all()])
        initial["technology"] = (", ").join([x.name for x in self.object.technology.all()])
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

    def form_valid(self, form):
        user = self.request.user if self.request.user.is_authenticated else None
        report = dict(self.request.POST)
        report.pop("csrfmiddlewaretoken", None)
        report = SuggestedEdit(
            organization=self.object,
            report=report,
            user=user,
            )
        
        report.save()
        return redirect(self.get_success_url())


class ReportViolationView(CreateView):
    template_name = "orgs/report.html" # TODO:Create Custom Template
    form_class = ViolationReportForm
    model = ViolationReport

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["organization"] = Organization.objects.get(slug=self.kwargs['slug'])
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.organization = Organization.objects.get(slug=self.kwargs['slug'])
        obj.user = self.request.user if self.request.user.is_authenticated else None
        return super().form_valid(form)
        

class UpdateOrgView(LoginRequiredMixin, UpdateView):
    """update form if organization is in organization"""
    template_name = "orgs/update.html"
    model = Organization
    form_class = OrgForm

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        initial["diversity"] = (", ").join([x.name for x in self.object.diversity.all()])
        initial["technology"] = (", ").join([x.name for x in self.object.technology.all()])
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
        

class ClaimOrgView(LoginRequiredMixin, DetailView):
    """Claim an organization if there are no organizers. This request must be reviewed."""
    template_name = "orgs/claim.html"
    model = Organization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if form.is_valid and request.user.is_authenticated:    
            self.object.organizers.add(request.user)
            self.object.save()

        return redirect(self.object.get_absolute_url())

class LocationFilterView(ListView):
    template_name = "orgs/list.html"
    model = Organization

    def get_queryset(self):
        return Organization.objects.filter(location__pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = Location.objects.get(pk=self.kwargs["pk"])
        return context


class DiversityFocusView(ListView):
    template_name = "tags/list.html"
    model = DiversityFocus
    paginate_by=50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['focus'] = 'diversity'
        context['focus_filter'] = 'diversity_filter'
        return context


class DiversityFocusFilterView(ListView):
    template_name = "orgs/list.html"
    model = Organization
    paginate_by=50

    def get_queryset(self):
        diversity=DiversityFocus.objects.get(name__iexact=self.kwargs["diversity"])
        queryset = Organization.objects.filter(diversity=diversity)
        if location:=self.request.GET.get('location', None):
            return queryset.filter(location=location) # Disconnect and filter by location
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = DiversityFocus.objects.get(name__iexact=self.kwargs["diversity"])
        context['focus'] = 'diversity'
        context["map"] = f"{context['focus']}_focus={context['tag'].id}"
        context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY

        if location:=self.request.GET.get('location', None):
            context["location"] = Location.objects.get(pk=location)
            context["map"] += f"&location={location}"
        
        return context

class TechnologyFocusView(ListView):
    template_name = "tags/list.html"
    model = TechnologyFocus
    paginate_by=25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["focus"] = "technology"
        context['focus_filter'] = 'technology_filter'
        return context
    

class TechnologyFocusFilterView(ListView):
    template_name = "orgs/list.html"
    model = Organization
    paginate_by: int = 25

    def get_queryset(self):
        """Filter by technology focus and location if provided."""
        orgs = Organization.objects.filter(technology__name__iexact=self.kwargs["technology"])
        
        if location:=self.request.GET.get('location', None):
            return orgs.filter(location__pk=location)
        
        return orgs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["focus"] = "technology"
        context["tag"] = TechnologyFocus.objects.get(name__iexact=self.kwargs["technology"])
        context["map"] = f"{context['focus']}_focus={context['tag'].id}"
        context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY


        if location:=self.kwargs.get('location', None):
            context["location"] = Location.objects.get(pk=location)
            context["map"] += f"&location={location}"
            
        return context


class OnlineTagFilterView(ListView):
    TAG_OPTIONS = {
        "diversity": DiversityFocus,
        "technology": TechnologyFocus
    }
    template_name = "orgs/list.html"
    model = Organization    

    def get_focus(self):
        """Gets the tag and tag_value from the url"""
        if (tag:=self.kwargs['tag'].lower()) in self.TAG_OPTIONS:
            return {
                'name': tag,
                'value': self.TAG_OPTIONS[tag].objects.get(pk=self.kwargs["tag_value"])
                }
        
        else:
            raise Http404("Tag not found.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.get_focus()
        return context

    def get_queryset(self):
        """Sets the queryset to diversity focus tags that are online."""
        tag = self.get_focus()
        return Organization.objects.filter(
                online_only=True,
                **{tag['name']: tag['value']}
        )


# class OnlineDiversityFocusFilterView(_OnlineTagFilterView):
#     pass

# class OnlineTechnologyFocusFilterView(ListView):
#     template_name = "orgs/list.html"
#     model = Organization

#     def get_queryset(self):
#         return Organization.objects.filter(diversity=self.kwargs["technology"])

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["location"] = "Online"
#         return context
