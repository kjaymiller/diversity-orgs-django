from django.contrib import admin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "username",)
    fieldsets = (
        (None, { 'fields': ('username', 'password', 'email', 'organizations',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)