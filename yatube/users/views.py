from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Обработчик запросов регистрации нового пользователя."""

    form_class = CreationForm
    success_url: str = reverse_lazy('posts:index')
    template_name: str = 'users/signup.html'
