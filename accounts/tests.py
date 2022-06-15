from django.test import TestCase
from .models import CustomUser
# Create your tests here.

class CustomUserTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = CustomUser.objects.create(
            username="test_user",
            email="test@example.com"
        )
    
    def test_user_str(self):
        self.assertEqual(str(self.user), self.user.username)