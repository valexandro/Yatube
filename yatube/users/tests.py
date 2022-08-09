from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .forms import CreationForm

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        self.user_1 = User.objects.create_user(username='TestUser1')
        self.authorized_client.force_login(self.user_1)

    def test_user_urls_uses_correct_template_and_available(self):
        """URL-адрес использует соответствующий шаблон и доступен.

        Адрес /auth/logout/ всегда должен быть в конце
        """
        url_template_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/NA/62e-c4d91fc988741bbe96c1/':
                'users/password_reset_confirm.html',
            '/auth/logout/': 'users/logged_out.html',
        }

        for address, template in url_template_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)


class UsersViewsTests(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        self.user_1 = User.objects.create_user(username='TestUser1')
        self.authorized_client.force_login(self.user_1)

    def test_views_uses_correct_template_and_available(self):
        """Вью использует соответствующий шаблон и доступен.

        Адрес /auth/logout/ всегда должен быть в конце
        """
        pages_templates_names = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={
                        'uidb64': 'NA',
                        'token': '62e-c4d91fc988741bbe96c1'
                    }):
                'users/password_reset_confirm.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)


class UsersContextTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_view_context(self):
        """В контексте страницы регистрации содержится CreationForm."""
        response = self.guest_client.get(reverse('users:signup'))
        form = response.context['form']
        self.assertIsInstance(form, CreationForm)


class UsersCreateFormTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """При заполнении формы 'users:signup' создаётся новый пользователь."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'ivan',
            'email': 'ivan@test.com',
            'password1': 'g939g%GGjs',
            'password2': 'g939g%GGjs',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='ivan',
            ).exists()
        )
