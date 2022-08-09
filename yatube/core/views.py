from django.shortcuts import render


def page_not_found(request, exception):
    """Кастомная страница 404 ошибки."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    """Кастомная страница 403 ошибки."""
    return render(request, 'core/403csrf.html')
