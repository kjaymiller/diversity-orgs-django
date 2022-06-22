from django.urls import path

from .views import CreateAPIKey, SignUpView, UpdateUserView, ResetAPIKey

urlpatterns = [
    path("signup", SignUpView.as_view(), name="account-signup"),
    path("update", UpdateUserView.as_view(), name="account-update"),
    path("reset-api-key", ResetAPIKey.as_view(), name="reset-api-key"),
    path("create-api-key", CreateAPIKey.as_view(), name="create-api-key"),
]
