from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_text = 'Тестовый постТестовый постТестовый пост'
        cls.test_group_title = 'Тестовая группа'
        cls.user: AbstractBaseUser = User.objects.create_user(
            username='TestUser')
        cls.group: Group = Group.objects.create(
            title=cls.test_group_title,
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post: Post = Post.objects.create(
            author=cls.user,
            text=cls.test_post_text,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.test_group_title, str(self.group))
        self.assertEqual(self.test_post_text[:15], str(self.post))

    def test_post_verbose_name(self):
        """verbose_name в полях постов совпадает с ожидаемым."""
        post_field_verbose = {
            'text': 'Текст поста',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }

        for field, expected_value in post_field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_post_help_texts(self):
        """help_text в полях постов совпадает с ожидаемым."""
        post_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        for field, expected_value in post_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)

    def test_group_verbose_name(self):
        """verbose_name в полях групп совпадает с ожидаемым."""
        group_field_verbose = {
            'title': 'Название',
            'slug': 'URL',
            'description': 'Описание',
        }
        for field, expected_value in group_field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value)
