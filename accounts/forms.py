from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from accounts.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")
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
    class Meta:
        model = CustomUser
        fields = ("username", "email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "border p-2 my-1 mx-3 w-96 focus:shadow"
        self.fields["username"].help_text = None
        self.fields.pop('password')