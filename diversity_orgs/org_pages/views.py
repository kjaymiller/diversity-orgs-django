from django.views.generic import ListView
from .models import Organization

# Create your views here.
class HomePageView(ListView):
    template_name = 'home.html'
    model = Organization