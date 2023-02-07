from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class StaticPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_exist_at_desired_location(self):
        about_urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in about_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_static_pages_accessible_by_name(self):
        about_names = [
            'about:author',
            'about:tech'
        ]
        for name in about_names:
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_static_pages_use_correct_template(self):
        templates_names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for name, template in templates_names.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
