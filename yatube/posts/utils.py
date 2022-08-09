from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest

from . import constants


def get_page_obj(request: HttpRequest, posts: QuerySet) -> Page:
    """Возвращает список постов для страницы паджинатора, переданной в URL."""
    paginator: Paginator = Paginator(posts, constants.POSTS_PER_PAGE)
    page_number: int = request.GET.get('page')
    return paginator.get_page(page_number)
