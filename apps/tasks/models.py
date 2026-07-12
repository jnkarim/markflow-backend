from django.conf import settings
from django.db import models


class Tag(models.Model):
    """A reusable, user-owned label attached to tasks."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    name = models.CharField(max_length=40)
    color = models.CharField(max_length=7, default="#FF8A00")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "name"),
                name="unique_tag_name_per_user",
            )
        ]

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    """A date-scoped Kanban task owned by one user."""

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    task_date = models.DateField(db_index=True)
    due_date = models.DateField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("status", "position", "created_at")
        indexes = [
            models.Index(
                fields=("user", "task_date", "status", "position"),
                name="task_board_lookup_idx",
            )
        ]

    def __str__(self) -> str:
        return self.title
