from typing import Dict, List, Type, Union

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post
from .utils import get_page_obj

User: Type[AbstractBaseUser] = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    """Обработчик запросов к главной странице сайта."""
    template: str = 'posts/index.html'
    posts: QuerySet = Post.objects.select_related('group', 'author')
    context: Dict = {
        'page_obj': get_page_obj(request, posts),
    }

    return render(request, template, context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Обработчик запросов к страницам групп."""
    template: str = 'posts/group_list.html'
    group: Group = get_object_or_404(Group, slug=slug)
    posts: QuerySet = group.posts.select_related('group', 'author')
    context: Dict = {
        'group': group,
        'page_obj': get_page_obj(request, posts),
    }

    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Обработчик запросов к странице профиля."""
    template: str = 'posts/profile.html'
    author: Union[AbstractBaseUser, AnonymousUser] = get_object_or_404(
        User, username=username)
    posts: QuerySet = author.posts.select_related('group')
    context: Dict = {
        'page_obj': get_page_obj(request, posts),
        'author': author,

    }
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Обработчик запросов к странице деталей поста."""
    template: str = 'posts/post_detail.html'
    post: Post = get_object_or_404(Post, id=post_id)
    form: CommentForm = CommentForm(request.POST or None)
    comments: List[Comment] = Comment.objects.filter(post=post)
    context: Dict = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Обработчик запросов создания поста."""
    template: str = 'posts/create_post.html'
    author: Union[AbstractBaseUser, AnonymousUser] = request.user
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,)
    if form.is_valid():
        instance: Post = form.save(commit=False)
        instance.author = author
        instance.save()
        return redirect('posts:profile', username=author.username)

    return render(request, template, {'form': form})


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Обработчик запросов редактирования поста."""
    template: str = 'posts/create_post.html'
    post: Post = get_object_or_404(Post, id=post_id)
    author: Union[AbstractBaseUser, AnonymousUser] = request.user
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if author != post.author:
        return redirect(post)

    if form.is_valid():
        form.save()
        return redirect(post)

    context: Dict = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Обработчик запросов добавления комментариев."""
    post: Post = get_object_or_404(Post, id=post_id)
    form: CommentForm = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
