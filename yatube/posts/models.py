from typing import Tuple, Type

from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.urls import reverse

User: Type[AbstractBaseUser] = get_user_model()


class Group(models.Model):
    """Модель группы, к которой может относиться пост."""

    title = models.CharField(
        max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        """Метаданные."""

        verbose_name: str = 'Группа'
        verbose_name_plural: str = 'Группы'

    def __str__(self) -> str:
        """Возвращает название группы."""
        return self.title


class Post(CreatedModel):
    """Модель поста."""

    text: models.TextField = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',)
    author: Type[AbstractBaseUser] = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """Метаданные."""

        ordering: Tuple[str] = ('-created', )
        verbose_name: str = 'Пост'
        verbose_name_plural: str = 'Посты'

    def __str__(self) -> str:
        """Возвращает текст поста."""
        return self.text[:15]

    def get_absolute_url(self):
        """Получение URL деталей поста."""
        return reverse('posts:post_detail', kwargs={'post_id': self.id, })


class Comment(CreatedModel):
    """Модель комментария к посту."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Пост к которому относится комментарий',
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )


class Follow(models.Model):
    """Модель подписок на посты других авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
