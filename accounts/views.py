from django.urls import reverse_lazy
from rest_framework.authtoken.models import Token
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.shortcuts import render, redirect
import django.contrib.messages


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("register")
    template_name = "registration/signup.html"

class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'registration/update.html'
    login_url = 'login'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['api_key'] = Token.objects.filter(user=self.request.user).first()
        return context

    def get_success_url(self):
        return reverse_lazy('account-update')

class CreateAPIKey(LoginRequiredMixin, TemplateView):
    login_url = 'login'

    def get(self, request):
        """Load the Create API Key page"""
        return render(request, 'registration/create_api_key.html')

    def post(self, request):
        """Check if the user already has an API key. If not create one."""
        if Token.objects.filter(user=request.user):
            django.contrib.messages.warning(request, 'You already have an API key. You can view it or reset it below.')
            return redirect('account-update')

        Token.objects.create(user=request.user)
        django.contrib.messages.success(request, 'API key has been created.')
        return redirect('account-update')
        
class ResetAPIKey(LoginRequiredMixin, TemplateView):
    login_url = 'login'

    def get(self, request):
        return render(request, 'registration/reset_api_key.html')

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        Token.objects.create(user=request.user)
        django.contrib.messages.success(request, 'API key has been reset.')
        return redirect('account-update')