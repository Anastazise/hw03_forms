from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(max_length=500, verbose_name='Текст')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True, on_delete=models.SET_NULL,
        verbose_name='Сообщество',
        related_name='posts')

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self) -> str:
        return self.text


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы')
    slug = models.SlugField(max_length=50, unique=True,
                            verbose_name='URL')
    description = models.TextField(max_length=500,
                                   verbose_name='Описание сообщества')
