from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    """Класс для создания групп."""
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Укажите желаемое название группы'
    )
    slug = models.SlugField(
        verbose_name='Фрагмент URL',
        help_text='Часть маршрута URL адреса группы',
        unique=True,
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Короткое описание группы',
    )

    class Meta:
        verbose_name = 'Группу'
        verbose_name_plural = 'Группы'

        """Метод для вывода строкового представления объекта."""
    def __str__(self):
        return self.title


class Post(CreatedModel):
    """Класс для создания постов."""
    text = models.TextField(
        verbose_name='Текст',
        help_text='Поле для ввода текста поста',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Указание автора поста',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Выбор группы, к которой относится пост',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Загрузите картинку',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    """Модель комментариев"""
    post = models.ForeignKey(
        Post,
        verbose_name='Ссылка на пост',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Поле для ввода текста поста',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    """Модель подписки на авторов"""
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
