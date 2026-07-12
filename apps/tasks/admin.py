from django.contrib import admin

from apps.tasks.models import Tag, Task


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "color", "created_at")
    search_fields = ("name", "user__email")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "task_date",
        "status",
        "priority",
        "position",
    )
    list_filter = ("status", "priority", "task_date")
    search_fields = ("title", "description", "user__email")
    filter_horizontal = ("tags",)
