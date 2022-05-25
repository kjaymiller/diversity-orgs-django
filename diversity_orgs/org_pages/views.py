from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView
from .models import Organization, ParentOrganization

# Create your views here.
class HomePageView(ListView):
    template_name = "home.html"
    model = ParentOrganization
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_orgs'] = ParentOrganization.objects.filter(featured=True)

class OrgListView(ListView):
    template_name = 'org_list.html'
    model = Organization

class OrgDetailView(DetailView):
    template_name = 'org_detail.html'
    model = Organization

class ParentOrgListView(ListView):
    template_name = 'parent_org_list.html'
    model = ParentOrganization

class ParentOrgDetailView(DetailView):
    template_name = 'parent_org_detail.html'
    model = ParentOrganization