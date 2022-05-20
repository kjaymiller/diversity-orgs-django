from django.views.generic import ListView
from .models import Organization, ParentOrganization

# Create your views here.
class OrgPageView(ListView):
    template_name = 'org_list.html'
    model = Organization


class ParentOrgPageView(ListView):
    template_name = 'parent_org_list.html'
    model = ParentOrganization