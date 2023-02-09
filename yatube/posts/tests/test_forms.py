import shutil
import tempfile
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
        )
        cls.unedited_post = Post.objects.filter(
            text=cls.post.text,
            group=cls.post.group,
            author=cls.post.author,
            pub_date=cls.post.pub_date,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_new_post_in_db(self):
        """
        Проверяем возможность создания поста разными
        типами пользователей и сохранение постов в базе данных.
        """
        posts_num = Post.objects.count()
        # гость
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_num)
        # пользователь
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
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_num + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/small.gif',
                author=self.user,
            )
            .exists()
        )

    def test_new_post_with_no_group_selected_in_db(self):
        """
        Проверяем возможность создания поста без указания группы
        и сохранение постов в базе данных.
        """
        posts_num = Post.objects.count()
        form_data = {
            'text': 'Второй тестовый текст'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_num + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=None,
                author=self.user,
            )
            .exists()
        )

    def test_edit_post_in_db_for_guest_client(self):
        """
        Проверяем возможность редактирования поста
        для гостя и сохранение изменений в базе данных.
        """
        form_data = {
            'text': 'Тестовый текст измененный',
            'group': self.group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        )
        self.assertTrue(self.unedited_post.exists())

    def test_edit_post_in_db_for_other_user(self):
        """
        Проверяем возможность редактирования поста не автором
        и сохранение изменений в базе данных.
        """
        form_data = {
            'text': 'Тестовый текст измененный',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.pk}/')
        self.assertTrue(self.unedited_post.exists())

    def test_edit_post_in_db_for_post_author(self):
        """
        Проверяем возможность редактирования поста автором
        и сохранение изменений в базе данных.
        """
        form_data = {
            'text': 'Тестовый текст измененный',
            'group': self.group.pk,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                **form_data,
                author=self.post.author,
                pub_date=self.post.pub_date,
                pk=self.post.pk
            )
            .exists()
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='no_name')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def test_new_comment_in_post(self):
        """
        Проверяем возможность написания комментария гостем
        и пользователем.
        """
        num_comments = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        # гость
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), num_comments)
        # пользователь
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), num_comments + 1)
        self.assertTrue(
            Comment.objects.filter(
                **form_data,
                author=self.user,
                post=self.post
            )
            .exists()
        )
