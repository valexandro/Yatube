from typing import Tuple

from django import forms
from django.db import models

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма создания и редактирования поста."""

    class Meta:
        """Метаданные формы."""

        model: models.Model = Post
        fields: Tuple[str, ...] = ('text', 'group', 'image',)


class CommentForm(forms.ModelForm):
    """Форма создания комментария к посту."""

    class Meta:
        """Метаданные формы."""

        model: models.Model = Comment
        fields: Tuple[str, ...] = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
