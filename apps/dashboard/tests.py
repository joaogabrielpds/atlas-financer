from django.test import TestCase
from django.urls import reverse

class DashboardTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
