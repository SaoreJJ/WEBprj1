from django.db import models
from users.models import User


class Course(models.Model):
    """
    Модель курса
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Название курса'
    )
    preview = models.ImageField(
        upload_to='courses/previews/',
        verbose_name='Превью',
        blank=True,
        null=True
    )
    description = models.TextField(
        verbose_name='Описание курса'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='Владелец'
    )
    last_update = models.DateTimeField(
        auto_now=True,
        verbose_name='Последнее обновление'
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-id']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """
    Модель урока
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Название урока'
    )
    description = models.TextField(
        verbose_name='Описание урока'
    )
    preview = models.ImageField(
        upload_to='lessons/previews/',
        verbose_name='Превью',
        blank=True,
        null=True
    )
    video_link = models.URLField(
        max_length=500,
        verbose_name='Ссылка на видео'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name='Владелец'
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['id']

    def __str__(self):
        return self.title
