from typing import Any, TypeVar
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Q, QuerySet
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from .models import (
    DiversityFocus,
    Organization,
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

def is_organizer(user: object, org:object) -> bool:
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


def get_tag_q(tag: str, value: str) -> Q:
    """Get a query for a tag and any parent tags"""
    return Q(**{f'{tag}__name__iexact': value}) | Q(**{f'{tag}__parents__name__in': value})


def get_location_q(params: dict[str, Any]) -> dict[Any]:
    """Get a query for a set of location parameters."""
    if "city" in params:
        params["name"] = params.pop('city')
    return {f'location__{key}__icontains': value for key, value in params.items() if value != None}
    

def validate_params(params: dict[str, Any]) -> dict[str, Any]:
    """Check params and remove invalid keys."""
    
    # tag filters check the tag name and the tag's parents
    valid_tags = (
        'diversity',
        'technology',
        'city',
        'region',
        'country',
        'active',
        'online_only',
        'paid',
    )
    
    return { t: params.get(t) for t in valid_tags if params.get(t, None) != None}    


def get_by_params(params: dict[str, Any], model: Organization=Organization,) -> QuerySet:
    """Get a queryset based on a set of parameters."""
    
    valid_params = validate_params(params)

    # tag filters check the tag name and the tag's parents
    location_params = {k:v for k,v in valid_params.items() if k in ("city", "region", "country")}
    bool_params = {k:v for k,v in valid_params.items() if k in ("active", "online_only", "paid")}
    queries = Q()

    for tag in ('diversity', 'technology'):
        if tag in valid_params: 
           queries |= get_tag_q(tag, valid_params[tag])

    # Combine all the filters
    for param in [bool_params, location_params, queries]:
        print(param)

    return model.objects.filter(
            queries,
            **bool_params,
            **get_location_q(location_params),
        ).distinct()

_context = TypeVar('_context', bound=dict)


# Create your views here.
class HomePageView(ListView):
    """The Home Page showing featured organizations and a map of all organizations."""
    
    template_name = "home.html"
    model = Organization

    def get_queryset(self) -> QuerySet[Organization]:
        """Return the organizations where the is_featured flag is True."""
        return self.model.objects.filter(is_featured=True) \
            .exclude(parent=None).values('parent__name', 'parent__slug') \
            .distinct().order_by()

    def get_context_data(self, **kwargs) -> _context:
        """
        Add aggregations from the object_list and the map API call trigger for `is_featured=True`
        """        

        context = super().get_context_data(**kwargs)

        context['aggs'] = [self.model.objects.get(name=obj['parent__name']) for obj in self.object_list]
        context["map"] = "is_featured=True"
        context["AZURE_MAPS_KEY"] = settings.AZURE_MAPS_KEY
        return context


class SearchResultsView(ListView):
    """Returns the results of a search query."""
    template_name = "search_results.html"
    model = Organization

    def get_queryset(self) -> SearchQuery:
        """
        Test search based on existed entrys in the database.
        Checks Organization, Location, DiversityFocus and TechnologyFocus objects.
        Returns a full text search on those models if nothing is a match.
        """
        
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

    def get_context_data(self, **kwargs) -> _context:
        """Add the search query and the parents aggregates to the context."""
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        context["parents"] = self.object_list.values("parent__name").distinct()
        return context

class OrgDetailView(DetailView):
    """Returns an organization's detail page."""
    template_name = "orgs/detail.html"
    model = Organization
    form_class = CreateOrgForm
    
    def get_context_data(self, **kwargs) -> _context:
        """
        Add the organization's parent and children to the context.
        Enable the map for all of the orgs children.
        Uses focuses and focus parents to build similar organizations.
        """
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
    """Create a new organization."""
    template_name = "orgs/create.html"
    model = Organization
    form_class = CreateOrgForm
    
    def get_success_url(self) -> str:
        """return the absolute url of the new organization."""
        return self.object.get_absolute_url()

    def post(self) -> HttpResponse:
        """Override the post method to add the user to the organization's list of organizers."""
        super().post()
        self.object.organizers.add(self.request.user)
        self.object.save()
        return redirect(self.get_success_url())


class SuggestEditView(UpdateView):
    """Form that allows users to suggest edits to an organization page."""
    template_name = "orgs/update.html" # TODO:Create #20 Custom Template
    form_class = SuggestEditForm
    model = Organization 

    def get_success_url(self) -> str:
        """Return the absolute url of the organization."""
        return self.object.get_absolute_url()
    
    def get_initial(self, *args, **kwargs) -> dict[str, Any]:
        """List all the tags, and organizers for the organization."""
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

    def form_valid(self) -> HttpResponse:
        """Override the form_valid method to add the user to the suggested edit."""
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
    """View that allows users to report a violation of an organization."""
    template_name = "orgs/report.html" # TODO:Create Custom Template
    form_class = ViolationReportForm
    model = ViolationReport

    def get_success_url(self) -> str:
        """
        Return the absolute url of the organization.

        Returns:
            str: absolute url of the organization
        """
        return self.object.get_absolute_url()

    def get_context_data(self, *args, **kwargs) -> _context:
        """Add the organization to the context"""
        context = super().get_context_data(*args, **kwargs)
        context["organization"] = Organization.objects.get(slug=self.kwargs['slug'])
        return context

    def form_valid(self, form: object) -> str:
        """
        Override the form_valid method to add the organization and user to the
        violation report prior to returning the success_url
        """
        obj = form.save(commit=False)
        obj.organization = Organization.objects.get(slug=self.kwargs['slug'])
        obj.user = self.request.user if self.request.user.is_authenticated else None
        return super().form_valid(form)
        

class UpdateOrgView(LoginRequiredMixin, UpdateView):
    """Update an existing organization"""
    template_name = "orgs/update.html"
    model = Organization
    form_class = OrgForm

    def get_initial(self, *args, **kwargs) -> dict[str, Any]:
        """
        Return the tags and organizers as strings in the form data.

        Returns:
            dict: initial data
        """
        initial = super().get_initial(*args, **kwargs)
        initial["diversity"] = (", ").join([x.name for x in self.object.diversity.all()])
        initial["technology"] = (", ").join([x.name for x in self.object.technology.all()])
        initial["organizers"] = (", ").join([x.email for x in self.object.organizers.all()])
    
        if self.object.parent:
            initial['parent'] = self.object.parent.name
    
        # Return the fetched data from Azure Maps instead of the supplied data from the users (initially)
        if self.object.location:
            location_fields = (
                self.object.location.name,
                self.object.location.region,
                self.object.location.country,
            )
            initial['location'] = ", ".join([x for x in location_fields if x])
        
        return initial
        
    def dispatch(self, request: object, *args, **kwargs) -> object:
        """Raise a 404 if user is not an organizer"""
        #TODO: #23 Can this be a TestMixin instead?

        if  is_organizer(request.user, self.get_object()):
            return super().dispatch(request, *args, **kwargs)
        raise Http404("You must be an organization member to update an organization.")
        

class ClaimOrgView(LoginRequiredMixin, CreateView):
    """
    Claim an organization if there are no organizers. This request must be reviewed.

    TODO: Create a type request for suggested edits and make claiming an org as an option.
    """
    template_name = "orgs/claim.html"
    model = SuggestedEdit
    # form_class = ClaimOrgForm # Not Implemented

    def get_success_url(self) -> str:
        """Return the absolute url of the organization."""
        return self.object.get_absolute_url()

    def get_context_data(self, *args, **kwargs) -> _context:
        """Add the organization to the context"""
        context = super().get_context_data(*args, **kwargs)
        context["organization"] = Organization.objects.get(slug=self.kwargs['slug'])
        return context

    def form_valid(self, form: object) -> str:
        """Override the form_valid method to add the organization and user to the violation report 
        prior to returning the success_url"""
        obj = form.save(commit=False)
        obj.organization = Organization.objects.get(slug=self.kwargs['slug'])
        obj.user = self.request.user if self.request.user.is_authenticated else None
        return super().form_valid(form)

    def dispatch(self, request: object, *args, **kwargs) -> object:
        """Raise a 404 if user is not an organizer"""

    def post(self, request: object, *args, **kwargs) -> str:
        """
        Override the post method to add the user to the organization as an organizer.
        WARNING: The logic for adding the user to the organization as an organizer has
        currently not been implemented and this should not be live.
        """
        self.object = self.get_object()

        if form.is_valid and request.user.is_authenticated:    
             # self.object.organizers.add(request.user)  DO NOT DO THIS AS IT WILL AUTOMATICALLY ADD THE USER AS AN ORGANIZER
            self.object.save()

        return redirect(self.object.get_absolute_url())


class DiversityFocusView(ListView):
    """List of the diversity focuses."""
    template_name = "tags/list.html"
    model = DiversityFocus
    paginate_by=50

    def get_context_data(self, **kwargs) -> _context:
        """
        Add a focus and focus_filter to the context.
        This can be used to distinguish diversity focuses from other tags.
        """
        context = super().get_context_data(**kwargs)
        context['focus'] = 'diversity'
        context['focus_filter'] = 'diversity_filter'
        return context


class TechnologyFocusView(ListView):
    """
    List of the technology focuses.

    Inheritance:
        ListView: Django BaseView for displaying a list of objects.
    """
    template_name = "tags/list.html"
    model = TechnologyFocus
    paginate_by=50

    def get_context_data(self, **kwargs) -> _context:
        """
        Add a focus and focus_filter to the context.
        This can be used to distinguish diversity focuses from other tags.
        """
        context = super().get_context_data(**kwargs)
        context["focus"] = "technology"
        context['focus_filter'] = 'technology_filter'
        return context
    

class TagFilterView(ListView):
    """
    Return a list  filtered by URL parameters.
    """
    TAG_OPTIONS = {
        "diversity": DiversityFocus,
        "technology": TechnologyFocus,
    }
    template_name = "orgs/list.html"
    model = Organization    
    paginate_by: int = 50

    def get_queryset(self) -> QuerySet:
        """Filter by the tag and tag_value"""
        return get_by_params(
            params=self.request.GET,
            model=Organization,
            )

    def get_context_data(self, **kwargs) -> _context:
        """add tag to context"""
        context = super().get_context_data(**kwargs)
        context = {
            **context,
            **validate_params(self.request.GET),
        }
        return context
        
