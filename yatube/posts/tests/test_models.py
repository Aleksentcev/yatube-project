from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment

SYMBOLS_NUM = 15

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст тестового поста',
        )

    def test_post_model_has_correct_object_name(self):
        """Проверяем, что у модели поста корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:SYMBOLS_NUM]
        self.assertEqual(expected_object_name, str(post))

    def test_post_model_verbose_names(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_post_model_help_texts(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_model_has_correct_object_name(self):
        """Проверяем, что у модели группы корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий',
            author=cls.user,
        )

    def test_comment_model_has_correct_object_name(self):
        """Проверяем, что у модели комментария корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_object_name = comment.text
        self.assertEqual(expected_object_name, str(comment))

    def test_comment_model_verbose_names(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Комментарий опубликован',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_model_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        help_text = comment._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Прокомментируйте пост')
