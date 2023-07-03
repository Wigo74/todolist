
from django.db import models
from django.utils import timezone

from core.models import User


class DatesModelMixin(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(verbose_name="Дата создания")
    updated = models.DateTimeField(verbose_name="Дата последнего обновления")

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super().save(*args, **kwargs)


class GoalCategory(DatesModelMixin):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)


class Goal(DatesModelMixin):
    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"

    class Status(models.IntegerChoices):
        to_do = 1, "К выполнению"
        in_progress = 2, "В процессе"
        done = 3, "Выполнено"
        archived = 4, "Архив"

    class Priority(models.IntegerChoices):
        low = 1, "Низкий"
        medium = 2, "Средний"
        high = 3, "Высокий"
        critical = 4, "Критический"

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="goals",
        on_delete=models.PROTECT,
    )
    category = models.ForeignKey(
        GoalCategory, verbose_name="Категория", on_delete=models.PROTECT
    )
    title = models.CharField(verbose_name="Заголовок", max_length=255)
    description = models.TextField(
        verbose_name="Описание", null=True, blank=True, default=None
    )
    due_date = models.DateField(
        verbose_name="Дата выполнения", null=True, blank=True, default=None
    )
    status = models.PositiveSmallIntegerField(
        verbose_name="Статус", choices=Status.choices, default=Status.to_do
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name="Приоритет", choices=Priority.choices, default=Priority.medium
    )

    def __str__(self):
        return self.title


class GoalComment(DatesModelMixin):
    class Meta:
        verbose_name = "Комментарий к цели"
        verbose_name_plural = "Комментарии к целям"

    user = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="goal_comments",
        on_delete=models.PROTECT,
    )
    goal = models.ForeignKey(
        Goal,
        verbose_name="Цель",
        related_name="goal_comments",
        on_delete=models.PROTECT,
    )
    text = models.TextField(verbose_name="Текст")





