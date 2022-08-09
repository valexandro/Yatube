from typing import Tuple

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import models

User = get_user_model()


class CreationForm(UserCreationForm):
    """Форма создания пользователя."""

    class Meta(UserCreationForm.Meta):
        """Метаданные формы создания пользователя."""

        model: models.Model = User
        fields: Tuple[str, ...] = (
            'first_name', 'last_name', 'username', 'email')
