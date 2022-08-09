import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment
from .utils import get_test_image

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.image_name_1 = 'test-image_1.png'
        cls.image_name_2 = 'test-image_2.png'

        cls.image_1 = get_test_image(cls.image_name_1)
        cls.image_2 = get_test_image(cls.image_name_2)

        cls.authorized_user = Client()
        cls.user: AbstractBaseUser = User.objects.create_user(
            username='TestUser')
        cls.authorized_user.force_login(cls.user)
        cls.group: Group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post_2: Post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 2',
            group=cls.group,
            image=cls.image_2,
        )

    def test_form_create_post(self):
        """При отправке формы со страницы создания поста пост создается.

        Так же происходит редирект на страницу пользователя
        """
        test_post_1_text = 'Тестовый пост 1'
        posts_count = Post.objects.count()
        form_data = {
            'text': test_post_1_text,
            'group': self.group.id,
            'image': self.image_1,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user.username}),
                             )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=test_post_1_text,
                group=self.group,
                image='posts/' + self.image_name_1,
            ).exists()
        )

    def test_form_edit_post(self):
        """При редактировании, происходит изменение поста в базе данных."""
        changed_post_2_text = 'Измененный тестовый пост 2'
        changed_post_form_data = {
            'text': changed_post_2_text,
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post_2.id}),
            data=changed_post_form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post_2.id}))

        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=changed_post_2_text,
                group=self.group,
                image='posts/' + self.image_name_2,
            ).exists())

    def test_form_add_comment(self):
        test_post_1_comment_1_text = 'Тестовый комментарий 1'
        comments_count = Comment.objects.count()
        form_data = {
            'text': test_post_1_comment_1_text,
        }
        response = self.authorized_user.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post_2.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post_2.id}),
                             )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                text=test_post_1_comment_1_text,
                post=self.post_2,
            ).exists()
        )
