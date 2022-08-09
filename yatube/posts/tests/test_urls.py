from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_user_1 = Client()
        cls.user_1: AbstractBaseUser = User.objects.create_user(
            username='TestUser1')
        cls.authorized_user_1.force_login(cls.user_1)

        cls.authorized_user_2 = Client()
        cls.user_2: AbstractBaseUser = User.objects.create_user(
            username='TestUser2')
        cls.authorized_user_2.force_login(cls.user_2)

        cls.guest_client = Client()

        cls.group: Group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post_1_user_1: Post = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост пользователя 1',
        )
        cls.index_url = '/'
        cls.post_create_url = '/create/'
        cls.post_1_edit_url = f'/posts/{cls.post_1_user_1.id}/edit/'
        cls.group_url = f'/group/{ cls.group.slug }/'
        cls.post_1_detail_url = f'/posts/{cls.post_1_user_1.id}/'
        cls.user_1_detail_url = f'/profile/{cls.user_1.username}/'
        cls.post_1_add_comment_url = f'/posts/{cls.post_1_user_1.id}/comment/'

    def test_urls_uses_correct_template_and_available(self):
        """URL-адрес использует соответствующий шаблон и доступен."""
        url_template_names = {
            self.index_url: 'posts/index.html',
            self.post_create_url: 'posts/create_post.html',
            self.post_1_edit_url: 'posts/create_post.html',
            self.group_url: 'posts/group_list.html',
            self.post_1_detail_url: 'posts/post_detail.html',
            self.user_1_detail_url: 'posts/profile.html',
        }

        for address, template in url_template_names.items():
            with self.subTest(address=address):
                response = self.authorized_user_1.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_url_redirect_anonymous(self):
        """Анонимный пользователь перенаправляется на страницу входа.

        На страницах с @login_required.
        """
        url_template = '/auth/login/?next={0}'
        restricted_url_template_names = {
            self.post_create_url: url_template.format(self.post_create_url),
            self.post_1_edit_url: url_template.format(self.post_1_edit_url),
            self.post_1_add_comment_url: url_template.format(
                self.post_1_add_comment_url)
        }

        for address, url in restricted_url_template_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, url)

    def test_nonexistent_page(self):
        """При переходе на несуществующую страницу возвращается код 404."""
        response = self.client.get('/made_up_url/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_edit_availability_only_to_author(self):
        """Редактирование поста доступно только автору."""
        response = self.authorized_user_1.get(
            self.post_1_edit_url,
            follow=True)

        self.assertEqual(
            response.status_code, HTTPStatus.OK)

    def test_redirect_of_non_author_to_post_details(self):
        """Не-автора перенаправляет на детали поста."""
        response = self.authorized_user_2.get(
            self.post_1_edit_url,
            follow=True)

        self.assertRedirects(
            response, self.post_1_detail_url
        )
