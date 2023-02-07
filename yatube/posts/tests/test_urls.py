from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Group, Post

INDEX_URL = '/'
GROUP_URL = '/group/test-slug/'
PROFILE_URL = '/profile/author/'
POST_CREATE_URL = '/create/'
UNEXISTING_PAGE = '/not_found/'
FOLLOW_URL = '/follow/'

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='no_name')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.author = User.objects.create_user(username='author')
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )

    def test_post_urls_exist_at_desired_location(self):
        """Проверяем доступность страниц любому пользователю."""
        posts_urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            f'/posts/{self.post.pk}/',
        ]
        for url in posts_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Проверяем  статус несуществующей страницы"""
        response = self.guest_client.get(UNEXISTING_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_page_and_redirect(self):
        """
        Проверяем доступность страницы создания поста
        только авторизованному пользователю.
        """
        # гость
        response = self.guest_client.get(POST_CREATE_URL, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        # пользователь
        response = self.authorized_client.get(POST_CREATE_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page_and_redirect(self):
        """
        Проверяем доступность страницы редактирования поста
        только автору поста.
        """
        post_edit_url = f'/posts/{self.post.pk}/edit/'
        # гость
        response = self.guest_client.get(post_edit_url, follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        )
        # не автор
        response = self.authorized_client.get(post_edit_url, follow=True)
        self.assertRedirects(response, f'/posts/{self.post.pk}/')
        # автор
        response = self.authorized_client_author.get(post_edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_page(self):
        response = self.authorized_client.get(FOLLOW_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_use_correct_templates(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            POST_CREATE_URL: 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            UNEXISTING_PAGE: 'core/404.html',
            FOLLOW_URL: 'posts/follow.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)
