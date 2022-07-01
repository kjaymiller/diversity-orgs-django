from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from uuid import uuid4
from django.utils.text import slugify
import httpx
import os
from accounts.models import CustomUser

def gen_upload_path():
    return f"media/logos/{uuid4()}/"


# Create your models here.
class DiversityFocus(models.Model):
    name = models.CharField(max_length=200)
    parents = models.ManyToManyField("self", blank=True, symmetrical=False)
    description = models.TextField(blank=True)
    other_names = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Diversity Focuses"


class TechnologyFocus(models.Model):
    name = models.CharField(max_length=200)
    parents = models.ManyToManyField("self", blank=True, symmetrical=False)
    other_names = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    region = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=250, blank=True, null=True)
    base_query = models.CharField(max_length=250, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=5, null=True, blank=True, unique=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=5, null=True, blank=True, unique=True)

    class Meta:
        ordering = ("country", "region", "name")

    def __str__(self):
        return f"{self.name}, {self.region}, {self.country}".replace("None", "").replace(", ,", ",")

    def save(self):
        if not self.latitude:
            response = httpx.get(
                url="https://atlas.microsoft.com/search/address/json",
                params={
                    "query": str(self.base_query),
                    "limit": 1,
                    "subscription-key": os.environ.get("AZURE_MAPS_KEY"),
                    "api-version": "1.0",
                },
            )

            if response.status_code == 200:
                result = response.json()["results"][0]
                self.country = result["address"]["country"]

                if "Municipality" in result["entityType"]:
                    self.name = result["address"]["municipality"]
                    self.region = result["address"].get(
                        "countrySubdivisionName", result["address"].get("countrySubdivison", "")
                    )

                self.latitude = result["position"]["lat"]
                self.longitude = result["position"]["lon"]
        return super().save()


class Organization(models.Model):
    USER_GROUP = 'USER_GROUP'
    EAP = "EMPLOYMENT ASSISTANCE PROGRAM"
    NETWORK = 'NETWORKING'
    MENTORSHIP = 'MENTORSHIP'
    CONFERENCE = 'CONFERENCE'
    YOUTH = 'YOUTH ORGANIZATION'
    CODE_SCHOOL = "CODE SCHOOL"
    OTHER = 'OTHER'

    TYPE_CHOICES = [
        (USER_GROUP, "User Group"),
        (EAP, "Employment Assistance Program"),
        (NETWORK, "Network"),
        (MENTORSHIP, "Mentorship"),
        (CONFERENCE, "Conference"),
        (YOUTH, "Youth Organization"),
        (CODE_SCHOOL, "Code School"),
        (OTHER, "Other"),
    ]
    org_type = models.CharField(
        choices=TYPE_CHOICES, default=USER_GROUP, max_length=50,
        blank=True, null=True,
    )
    slug = models.SlugField(
        max_length=200, unique=True, null=True,
        help_text="Slug will be generated automatically from the name of the organization.",
        )
    name = models.CharField(
        max_length=200, unique=True,
        help_text="Name of the organization.",
        )
    code_of_conduct = models.URLField(
        blank=True, verbose_name="Code of Conduct",
        help_text="URL to the code of conduct for the organization.",
        )
    description = models.TextField(
        blank=True,
        help_text="Description of the organization. This will appear on the organization's page.",
        )
    diversity = models.ManyToManyField(
        DiversityFocus, related_name="parent_org_diversity", blank=True,
        help_text="Diversity focuses for the organization. Select as many as apply. The more specific the better. Examples: Black Women, LGBTQIA+",
    )
    job_board = models.URLField(
        blank=True,
        help_text="URL to the job board for the organization.",
    )
    paid = models.BooleanField(
        default=False,
        help_text="Do members have to pay for membership?",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="(ADMINS ONLY) Is this organization featured on the home page?",
    )
    url = models.URLField(
        blank=True, null=True,
        help_text="URL to the organization's website.",
    )
    social_links = ArrayField(
        base_field=models.URLField(),
        default=list,
        help_text="Social media links for the organization. Put each url on a new line.",
        )
    events_link = models.URLField(
        blank=True,
        help_text="URL to the organization's events page.",
    )
    active = models.BooleanField(
        default=True,
        help_text="Is this organization active? Inactive organizations will be marked and filtered out.",
    )
    organizers = models.ManyToManyField(
        CustomUser, blank=True, related_name="organizers",
        help_text="Users who are organizers of this organization.",
       )
    reviewed = models.BooleanField(
        default=False,
        help_text="(ADMIN Only) Has this organization been reviewed?",
    )
    online_only = models.BooleanField(
        default=False,
        help_text="Is this organization only available online?",
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Location of the organization. Format: city, Optional(state/region), country",
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True,
        help_text="Is this organization a sub-organization of another org? NOTE:The Parent Org Must exist before this org can be created.",
    )
    technology = models.ManyToManyField(
        TechnologyFocus, blank=True, related_name="parent_org_technology",
        help_text="Technology focuses for the organization. If your org doesn't focus on a particular tech topic, Leave Blank",
    )
    logo = models.ImageField(
        upload_to=gen_upload_path(), blank=True,
        help_text="Logo of the organization. Will be displayed on the organization's page.",
    )


    class Meta:
        ordering = ("name",)

    def save(self):
        super().save()

    def get_from_parents(self):
        if self.parent:
            if not self.logo:
                self.logo = self.parent.logo

            if self.name == self.parent.name:
                self.name = f"{self.name} {self.location.name}"

            if not self.description:
                self.description = self.parent.description

            if not self.code_of_conduct:
                self.code_of_conduct = self.parent.code_of_conduct

            if not self.diversity.all():
                self.diversity.set(self.parent.diversity.all())

            if not self.technology.all():
                self.technology.set(self.parent.technology.all())

        if not self.slug:
            self.slug = slugify(self.name)

        return super().save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("org_detail", kwargs={"slug": self.slug})

    def set_children_focuses(self):
        for obj in Organization.objects.filter(parent=self):
            obj.description = self.description
            obj.diversity.set(self.diversity.all())
            obj.technology.set(self.technology.all())
            if not obj.logo:
                obj.logo = self.logo
            obj.save()


class SuggestedEdit(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL,
        help_text="Organization the edit should go to.",
        null=True,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        help_text="User who suggested the edit.",
        null=True,
    )
    report = models.JSONField()

    def get_absolute_url(self):
        return reverse("org_detail", kwargs={"slug": self.organization.slug})
    
    def __str__(self):
        user = self.user or "Anonymous"
        return f"{self.organization.name} - {user}"


class OrgClaim(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL,
        help_text="Organization the claim should go to.",
        null=True,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        help_text="User who suggested the claim.",
        null=True,
    )
    description = models.TextField(
        help_text="What information can we use to validate your claim?",
    )

    def get_absolute_url(self):
        return reverse("org_detail", kwargs={"slug": self.organization.slug})
    
    def __str__(self):
        user = self.user or "Anonymous"
        return f"{self.organization.name} - {user}"

class ViolationReport(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL,
        help_text="Organization accused of violation.",
        null=True,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        help_text="User who reported the violation.",
        null=True,
    )
    report = models.TextField(
        help_text="Report of the violation.",
    )

    def get_absolute_url(self):
        return reverse("org_detail", kwargs={"slug": self.organization.slug})