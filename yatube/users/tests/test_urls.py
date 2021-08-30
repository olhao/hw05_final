from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

User = get_user_model()


class UserTestURLS(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup_page(self):
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_page(self):
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_page(self):
        response = self.guest_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_page(self):
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_page(self):
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_page(self):
        response = self.guest_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_page(self):
        response = self.guest_client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_reset_done_page(self):
        response = self.guest_client.get('/auth/reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template_for_guest_client(self):
        templates_url_names = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/logged_out.html': '/auth/logout/',
            'users/password_reset_form.html': '/auth/password_reset/',
            'users/password_reset_done.html': '/auth/password_reset/done/',
            'users/password_reset_complete.html': '/auth/reset/done/',
        }

        for template_key, address_value in templates_url_names.items():
            with self.subTest(address=address_value):
                response = self.guest_client.get(address_value)
                self.assertTemplateUsed(response, template_key)

    def test_urls_uses_correct_template_for_authorized_client(self):
        templates_url_names = {
            'users/password_change_form.html': '/auth/password_change/',
            'users/password_change_done.html': '/auth/password_change/done/',
        }

        for template_key, address_value in templates_url_names.items():
            with self.subTest(address=address_value):
                response = self.authorized_client.get(address_value)
                self.assertTemplateUsed(response, template_key)
