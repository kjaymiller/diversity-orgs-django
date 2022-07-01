from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from .models import (
    Organization,
    Location,
    DiversityFocus,
    TechnologyFocus,
    SuggestedEdit,
    ViolationReport,
    )
from accounts.models import CustomUser


class OrgForm(forms.ModelForm):
    template_name = "forms/org_form.html"
    social_links = SimpleArrayField(
            forms.CharField(
                widget=forms.Textarea(
                    attrs={'rows':4, 'cols':25}
                ),
                max_length=200),
            delimiter='\n',
            required=False,
            )
    location = forms.CharField(label="Location", required=False, empty_value=None)
    diversity = forms.CharField(
        help_text=Organization._meta.get_field('diversity').help_text,
        label="Diversity Focuses", required=False,
    )
    technology = forms.CharField(
        help_text=Organization._meta.get_field('technology').help_text,
        label="Technology Focuses", required=False,
        )
    organizers = forms.CharField(
        help_text=Organization._meta.get_field('organizers').help_text,
        widget=forms.Textarea(attrs={'rows':3, 'cols':25}), required=False, empty_value=''
        )
    parent = forms.CharField(
        help_text=Organization._meta.get_field('parent').help_text,
        label="Parent Organization", required=False, empty_value=None,
        )


    class Meta:
        model = Organization
        exclude = ('is_featured', 'reviewed')
        widgets = {'paid': forms.Select(choices=((True, 'Yes'), (False, 'No')))}

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "rounded border p-1 my-1 mx-3 w-96 focus:shadow border-slate-300"
            
    def clean(self):
        for field_name, model in (('diversity', DiversityFocus), ('technology', TechnologyFocus)):
            if self.cleaned_data.get(field_name):
                values = [x.strip() for x in self.cleaned_data.pop(field_name).split(",")]
                self.cleaned_data[field_name] = [model.objects.get_or_create(defaults={'name': x}, name__iexact=x)[0] for x in values]

        if self.cleaned_data.get('parent'):
            parent = Organization.objects.get(name=self.cleaned_data.get('parent'))
            self.cleaned_data['parent'] = parent

        if self.cleaned_data.get('organizers'):
            values = [x.strip() for x in self.cleaned_data.pop("organizers").split("\n")]
            self.cleaned_data['organizers'] = [CustomUser.objects.get(email__iexact=x) for x in values]

        if self.cleaned_data.get('location'): 
            form_location = self.cleaned_data.pop("location")

            if form_location:
                location = Location.objects.get_or_create(base_query__icontains=form_location)[0]
                self.cleaned_data['location'] = location

class CreateOrgForm(OrgForm):
    template_name = "forms/org_form.html"

    class Meta:
        model = Organization
        exclude = ('slug', "organizers", "reviewed", "is_featured", "active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Organization Name'
        self.fields['code_of_conduct'].widget.attrs['placeholder'] = 'URL to your Code of Conduct'
        for field in self.fields.values():
            field.widget.attrs["class"] = "border my-1 p-1 mx-3 w-96 focus:shadow"


class SuggestEditForm(OrgForm):
    id = forms.IntegerField(widget=forms.HiddenInput())
    template_name = "forms/org_form.html"

    class Meta:
        model = Organization
        exclude = (
            'slug', "organizers", "reviewed", "is_featured", 'parent', 'logo', 'active',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "border my-1 mx-3 w-96 focus:shadow"


class ViolationReportForm(forms.ModelForm):
    template_name = "forms/org_form.html"

    class Meta:
        model = ViolationReport
        exclude = ('user', 'organization')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "border my-1 mx-3 w-96 focus:shadow"