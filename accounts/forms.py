from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm

from accounts.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    field_order = ["username", "password1", "password2", "email", "twitter", "github", "linkedin", "agrees_to_coc"]
    template_name = "forms/org_form.html"

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'twitter', 'github', 'linkedin', 'agrees_to_coc')
        model = CustomUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "border my-1 mx-3 w-96 focus:shadow"
        self.fields["password1"].help_text = "at least 8 characters"
        self.fields["username"].help_text = None


class AdminUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"

class CustomUserChangeForm(UserChangeForm):
    template_name = "forms/org_form.html"

    class Meta:
        model = CustomUser
        fields = ("username", "email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "border p-2 my-1 mx-3 w-96 focus:shadow"
        self.fields["username"].help_text = None
        self.fields.pop('password')


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs["class"] = "border p-1 rounded my-1 m-3 w-96 focus:shadow"
            field.widget.attrs['placeholder'] = field.label