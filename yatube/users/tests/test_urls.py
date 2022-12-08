from django.test import Client, TestCase


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'users/logged_out.html': 'logout/',
            'users/login.html': 'login/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)