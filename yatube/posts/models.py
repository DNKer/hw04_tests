from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.fields.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    slug = models.fields.SlugField(
        max_length=255,
        unique=True,
        verbose_name='Заголовок'
    )
    description = models.fields.TextField(
        max_length=255,
        verbose_name='Описание'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст публикации'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )

    group = models.ForeignKey(
        Group,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой относится публикация'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        text_limit: int = 15
        return self.text[:text_limit]
