import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.core.cache import cache
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .. import constants
from ..forms import PostForm
from ..models import Comment, Group, Post
from .utils import get_test_image

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()
        cls.user: AbstractBaseUser = User.objects.create_user(
            username='TestUser')
        cls.authorized_client.force_login(cls.user)

        cls.group: Group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post: Post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cache.clear()

    def test_views_uses_correct_template_and_available(self):
        """Вью использует соответствующий шаблон и доступен."""
        pages_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }

        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsContextViewTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.image_name = 'test-image.png'
        cls.image = get_test_image(cls.image_name)

        cls.authorized_client = Client()
        cls.user: AbstractBaseUser = User.objects.create_user(
            username='TestUser')
        cls.authorized_client.force_login(cls.user)
        cls.group: Group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post: Post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.image,
        )
        cls.comment: Comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )
        cache.clear()

    def assert_post_equal_to_test_post(self, context, has_paginator=False):
        """Проверка переданного в контексте поста на соответствие тестовому."""
        if has_paginator:
            paginator_page: Page = context['page_obj']
            post_to_check: Post = paginator_page[0]
        else:
            post_to_check = context['post']
        self.assertEqual(post_to_check.author, self.post.author)
        self.assertEqual(post_to_check.text, self.post.text)
        self.assertEqual(post_to_check.created, self.post.created)
        self.assertEqual(post_to_check.group, self.post.group)
        self.assertEqual(post_to_check.image, self.post.image)
        self.assertEqual(post_to_check.pk, self.post.pk)
        self.assertEqual(post_to_check.image, self.post.image)

    def assert_group_equal_to_test_group(self, context):
        """Проверка переданной в контексте группы на соответствие тестовой."""
        group_to_check: Group = context['group']
        self.assertEqual(group_to_check.title, self.group.title)
        self.assertEqual(group_to_check.slug, self.group.slug)
        self.assertEqual(group_to_check.description, self.group.description)
        self.assertEqual(group_to_check.pk, self.group.pk)

    def test_index_context(self):
        """Контекст домашней страницы.

        Должен быть паджинатор с тестовым постом.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        self.assert_post_equal_to_test_post(
            response.context, has_paginator=True)

    def test_group_list_page_correct_context(self):
        """Контекст страницы группы.

        Должен быть паджинатор с тестовыми постом и группой.
        """
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))

        self.assert_group_equal_to_test_group(response.context)
        self.assert_post_equal_to_test_post(
            response.context, has_paginator=True)

    def test_profile_page_correct_context(self):
        """Контекст страницы профиля.

        Должен быть паджинатор с тестовыми постом и автором.
        """
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))

        user: AbstractBaseUser = response.context['author']

        self.assertEqual(user.pk, self.user.pk)
        self.assert_post_equal_to_test_post(
            response.context, has_paginator=True)

    def test_post_detail_page_correct_context(self):
        """Контекст страницы деталей поста.

        Должен быть объект нужного поста
        """
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        test_comment: Comment = response.context.get('comments')[0]

        self.assertEqual(test_comment.pk, self.comment.pk)
        self.assertEqual(test_comment.author, self.user)
        self.assertEqual(test_comment.text, self.comment.text)

        self.assert_post_equal_to_test_post(
            response.context)

    def test_post_create_page_correct_context(self):
        """Контекст страницы создания поста.

        Должен быть объект формы создания поста.
        """
        response = self.authorized_client.get(
            reverse('posts:post_create'))

        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_page_correct_context(self):
        """Контекст страницы редактирования поста.

        Должен быть объект формы создания поста, поста, и is_edit==True.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))

        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['is_edit'])
        self.assert_post_equal_to_test_post(
            response.context)


class PaginatorViewsTest(TestCase):
    @ classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.POSTS_ON_SECOND_PAGE = 3

        cls.authorized_client = Client()
        cls.user: AbstractBaseUser = User.objects.create_user(
            username='TestUser')
        cls.authorized_client.force_login(cls.user)

        cls.group: Group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.num_of_test_posts = (
            constants.POSTS_PER_PAGE + cls.POSTS_ON_SECOND_PAGE)

        Post.objects.bulk_create(
            [Post(
                pk=i,
                author=cls.user,
                group=cls.group,
                text='Тестовый пост ' + str(i))
                for i in range(cls.num_of_test_posts)])

        cls.paginator_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username}),
        ]
        cache.clear()

    def test_pages_contains_correct_number_of_records(self):
        """Паджинатор содержит корректное количество постов на страницах."""
        pages_posts = {
            '': constants.POSTS_PER_PAGE,
            '2': self.POSTS_ON_SECOND_PAGE,
        }

        for reverse_name in self.paginator_pages:
            for page_number, posts_on_page in pages_posts.items():
                with self.subTest(page_number=page_number,
                                  reverse_name=reverse_name):
                    response = self.authorized_client.get(
                        reverse_name, {'page': page_number})
                    posts = response.context['page_obj']
                    self.assertEqual(len(posts), posts_on_page)

    def test_paginator_first_post(self):
        """Первым отображается самый новый пост."""
        for reverse_name in self.paginator_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post_12: Post = response.context.get('page_obj').object_list[0]
                self.assertEqual(
                    post_12.text, f'Тестовый пост {self.num_of_test_posts-1}')


class PostLocationViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user_1: AbstractBaseUser = User.objects.create_user(
            username='TestUser1')
        cls.user_2: AbstractBaseUser = User.objects.create_user(
            username='TestUser2')

        cls.group_1: Group = Group.objects.create(
            title='Тестовая группа_1',
            slug='test_slug_1',
            description='Тестовое описание_1',
        )
        cls.group_2: Group = Group.objects.create(
            title='Тестовая группа_2',
            slug='test_slug_2',
            description='Тестовое описание_2',
        )
        cls.post_group_1_user_1: Post = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост 1',
            group=cls.group_1

        )
        cls.post_group_2_user_2: Post = Post.objects.create(
            author=cls.user_2,
            text='Тестовый пост 2',
            group=cls.group_2
        )
        cache.clear()

    def test_posts_appear_in_correct_groups(self):
        """Пост появляется на корректных страницах групп."""
        response_group_1 = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_1.slug}))
        response_group_2 = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug}))

        group_1_posts: Page = response_group_1.context.get('page_obj')
        group_2_posts: Page = response_group_2.context.get('page_obj')

        self.assertIn(self.post_group_1_user_1, group_1_posts)
        self.assertIn(self.post_group_2_user_2, group_2_posts)

        self.assertNotIn(self.post_group_1_user_1, group_2_posts)
        self.assertNotIn(self.post_group_2_user_2, group_1_posts)

    def test_posts_appear_for_correct_users(self):
        """Пост появляется на корректных страницах пользователей."""
        response_user_1 = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user_1.username}))
        response_user_2 = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user_2.username}))

        user_1_posts: Page = response_user_1.context.get('page_obj')
        user_2_posts: Page = response_user_2.context.get('page_obj')

        self.assertIn(self.post_group_1_user_1, user_1_posts)
        self.assertIn(self.post_group_2_user_2, user_2_posts)

        self.assertNotIn(self.post_group_1_user_1, user_2_posts)
        self.assertNotIn(self.post_group_2_user_2, user_1_posts)

    def test_posts_on_home_page(self):
        """Посты разных групп и пользователей появляются на главной."""
        response = self.guest_client.get(reverse('posts:index'))

        homepage_posts: Page = response.context.get('page_obj')

        self.assertIn(self.post_group_1_user_1, homepage_posts)
        self.assertIn(self.post_group_2_user_2, homepage_posts)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user: AbstractBaseUser = User.objects.create_user(
            username='TestUser')

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post_1: Post = Post.objects.create(
            author=cls.user,
            text='Изначальный пост'

        )
        cache.clear()

    def test_index_page_cache(self):
        """Кеширование на главной странице работает."""
        new_post_text = 'Новый пост'
        self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.user,
            text=new_post_text,
        )
        updated_response_1 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotContains(updated_response_1, new_post_text)

        cache.clear()

        updated_response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(updated_response_2, new_post_text)
