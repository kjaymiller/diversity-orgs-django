from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CreateAPIKey, SignUpView, UpdateUserView, ResetAPIKey
from .forms import LoginForm
urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=LoginForm,
        ),
        name="login",
    ),
    path("signup", SignUpView.as_view(), name="account-signup"),
    path("update", UpdateUserView.as_view(), name="account-update"),
    path("reset-api-key", ResetAPIKey.as_view(), name="reset-api-key"),
    path("create-api-key", CreateAPIKey.as_view(), name="create-api-key"),
]
