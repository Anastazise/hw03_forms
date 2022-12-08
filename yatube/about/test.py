from http import HTTPStatus
from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_and_tech(self):
        """Проверяем, доступность страниц about/author и about/tech."""
        urls = (
            '/about/author/',
            '/about/tech/',
        )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_404(self):
        """Проверяем, запрос к несуществующей странице."""
        response = self.guest_client.get('/page_404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)