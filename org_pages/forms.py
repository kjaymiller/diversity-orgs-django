from django import forms
from .models import Organization

class OrgForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ('is_featured',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "border my-1 mx-3 w-96 focus:shadow"
        

class CreateOrgForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ('slug', 'is_featured',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Organization Name'
        self.fields['code_of_conduct'].widget.attrs['placeholder'] = 'URL to your Code of Conduct'
        for field in self.fields.values():
            field.widget.attrs["class"] = "border my-1 mx-3 w-96 focus:shadow"
