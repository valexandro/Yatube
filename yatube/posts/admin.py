from django.contrib import admin

from .models import Comment, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройка отображения постов в админке."""

    list_display = ('pk', 'text', 'created', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Настройка отображения групп в админке."""

    list_display = ('title', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class GroupAdmin(admin.ModelAdmin):
    """Настройка отображения комментариев в админке."""

    list_display = ('text', 'author', 'created',)
    empty_value_display = '-пусто-'
