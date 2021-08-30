from django.test import Client, TestCase
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_author_page(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_technology_page(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template_key, address_value in templates_url_names.items():
            with self.subTest(address=address_value):
                response = self.guest_client.get(address_value)
                self.assertTemplateUsed(response, template_key)
