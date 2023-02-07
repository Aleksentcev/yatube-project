import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..forms import PostForm, CommentForm
from ..models import Group, Post, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

NUM_OF_TEST_POSTS = 12
NUM_OF_SHOWING_POSTS = 10
NUM_OF_POSTS_ON_PAGE_TWO = 2
INDEX = 'posts:index'
GROUP_LIST = 'posts:group_list'
PROFILE = 'posts:profile'
POST_DETAIL = 'posts:post_detail'
POST_CREATE = 'posts:post_create'
POST_EDIT = 'posts:post_edit'
FOLLOW_INDEX = 'posts:follow_index'
FOLLOW = 'posts:profile_follow'
UNFOLLOW = 'posts:profile_unfollow'


User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
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

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )

        cls.group_2 = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test-slug-2',
            description='Тестовое описание второй группы'
        )

        for i in range(NUM_OF_TEST_POSTS):
            Post.objects.create(
                text='Тестовый пост первой группы',
                author=cls.user,
                group=cls.group
            )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост второй группы',
            author=cls.author,
            group=cls.group_2,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий.',
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_pages_use_correct_templates(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse(INDEX): 'posts/index.html',
            reverse(
                GROUP_LIST, kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                PROFILE, kwargs={'username': self.author.username}
            ): 'posts/profile.html',
            reverse(
                POST_DETAIL, kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(POST_CREATE): 'posts/create_post.html',
            reverse(
                POST_EDIT, kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse(FOLLOW_INDEX): 'posts/follow.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Проверяем, что шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.guest_client.get(reverse(INDEX))
        expected = list(Post.objects.all().order_by(
            '-pub_date'))[:NUM_OF_SHOWING_POSTS]
        self.assertEqual(list(response.context['page_obj']), expected)
        self.assertEqual(Post.objects.first().image, self.post.image)

    def test_group_list_page_shows_correct_context(self):
        """
        Проверяем, что шаблон group_list сформирован с правильным контекстом.
        """
        response = self.guest_client.get(reverse(
            GROUP_LIST, kwargs={'slug': self.group.slug}))
        expected = list(self.group.posts.all().order_by(
            '-pub_date'))[:NUM_OF_SHOWING_POSTS]
        self.assertEqual(list(response.context['page_obj']), expected)
        self.assertEqual(response.context.get('group'), self.group)
        self.assertEqual(Post.objects.first().image, self.post.image)

    def test_profile_page_shows_correct_context(self):
        """
        Проверяем, что шаблон profile сформирован с правильным контекстом.
        """
        response = self.guest_client.get(reverse(
            PROFILE, kwargs={'username': self.user.username}))
        expected = list(self.user.posts.all().order_by(
            '-pub_date'))[:NUM_OF_SHOWING_POSTS]
        self.assertEqual(list(response.context['page_obj']), expected)
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(Post.objects.first().image, self.post.image)

    def test_post_detail_page_shows_correct_context(self):
        """
        Проверяем, что шаблон post_detail сформирован с правильным контекстом.
        """
        comments = list(self.post.comments.all())
        response = self.authorized_client_author.get(reverse(
            POST_DETAIL, kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').image, self.post.image)
        self.assertEqual(list(response.context.get('comments')), comments)
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_post_edit_page_shows_correct_context(self):
        """
        Проверяем, что шаблон post_edit сформирован с правильным контекстом.
        """
        response = self.authorized_client_author.get(reverse(
            POST_EDIT, kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get('post_id'), int(self.post.pk))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context.get('is_edit'))

    def test_create_post_page_shows_correct_context(self):
        """
        Проверяем, что шаблон create_post сформирован с правильным контекстом.
        """
        response = self.authorized_client_author.get(reverse(POST_CREATE))
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertFalse(response.context.get('is_edit'))

    def test_post_correct_appears(self):
        """
        Проверяем, что созданный пост появляется на определенных страницах.
        """
        cache.clear()
        self.authorized_client.get(
            reverse(FOLLOW, kwargs={'username': self.author.username})
        )
        pages = [
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': self.group_2.slug}),
            reverse(PROFILE, kwargs={'username': self.author.username}),
            reverse(FOLLOW_INDEX),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertContains(response, self.post)

    def test_post_does_not_appear_on_other_pages(self):
        """
        Проверяем, что созданный пост не появляется на других страницах.
        """
        cache.clear()
        pages = [
            reverse(GROUP_LIST, kwargs={'slug': self.group.slug}),
            reverse(PROFILE, kwargs={'username': self.user.username}),
            reverse(FOLLOW_INDEX),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertNotContains(response, self.post)

    def test_index_cache(self):
        cache.clear()
        post = Post.objects.create(
            text='Тестовый пост для проверки кеша',
            author=self.author,
        )
        response = self.guest_client.get(reverse(INDEX))
        self.assertContains(response, post.text)
        post.delete()
        response = self.guest_client.get(reverse(INDEX))
        self.assertContains(response, post)

    def test_follow_and_unfollow(self):
        """
        Проверяем возможность пользователя подписаться
        на другого пользователя и отписаться от него.
        """
        self.authorized_client.get(
            reverse(FOLLOW, kwargs={'username': self.author.username})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            )
            .exists()
        )
        self.authorized_client.get(
            reverse(UNFOLLOW, kwargs={'username': self.author.username})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            )
            .exists()
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        for i in range(NUM_OF_TEST_POSTS):
            Post.objects.create(
                text='Тестовый пост группы',
                author=cls.author,
                group=cls.group
            )

    def test_first_page_contains_ten_posts(self):
        pages = [
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': self.group.slug}),
            reverse(PROFILE, kwargs={'username': self.author.username})
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
        self.assertEqual(
            len(response.context['page_obj']),
            NUM_OF_SHOWING_POSTS
        )

    def test_second_page_contains_two_posts(self):
        pages = [
            reverse(GROUP_LIST, kwargs={'slug': self.group.slug}),
            reverse(PROFILE, kwargs={'username': self.author.username})
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            NUM_OF_POSTS_ON_PAGE_TWO
        )
