from urllib import response
from django.test import TestCase
from .models import Organization

# Create your tests here.
class OrganizationPageTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.org = Organization.objects.create(
            name="Test Organization",
            description="Test description",
            url="https://www.test.org",
        )

    def get_response(self):
        response = self.client.get('/')
        return response

    def test_org_page_status_code(self):
        self.assertEqual(self.get_response().status_code, 200)

    def test_org_page_template(self):
        self.assertTemplateUsed(self.get_response(), 'org_list.html')

    def test_org_page_contains_org_name(self):
        self.assertContains(self.get_response(), self.org.name)

