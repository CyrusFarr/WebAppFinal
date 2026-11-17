from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class HomePageTests(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_home_page_content(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Welcome to PortfolioIQ")
