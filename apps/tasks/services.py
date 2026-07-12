"""Business logic for task board operations."""

from django.db import transaction
from django.utils import timezone

from apps.tasks.models import Task


def _normalize_column(tasks: list[Task], *, status: str) -> None:
    """Assign contiguous positions to a column and persist them efficiently."""

    if not tasks:
        return

    updated_at = timezone.now()
    for position, task in enumerate(tasks):
        task.status = status
        task.position = position
        task.updated_at = updated_at

    Task.objects.bulk_update(tasks, ("status", "position", "updated_at"))


@transaction.atomic
def reorder_task(*, user, task_id: int, status: str, position: int) -> Task:
    """Move an owned task within or between date-scoped Kanban columns.

    Rows involved in the source and destination columns are locked for the
    duration of the transaction. This prevents overlapping reorder requests
    from leaving duplicate or missing positions.
    """

    task = Task.objects.select_for_update().get(pk=task_id, user=user)
    board_tasks = Task.objects.select_for_update().filter(
        user=user,
        task_date=task.task_date,
    )

    source_tasks = list(
        board_tasks.filter(status=task.status)
        .exclude(pk=task.pk)
        .order_by("position", "created_at", "pk")
    )

    if task.status == status:
        destination_tasks = source_tasks
    else:
        destination_tasks = list(
            board_tasks.filter(status=status)
            .exclude(pk=task.pk)
            .order_by("position", "created_at", "pk")
        )

    target_position = min(position, len(destination_tasks))
    destination_tasks.insert(target_position, task)

    if task.status != status:
        _normalize_column(source_tasks, status=task.status)

    _normalize_column(destination_tasks, status=status)

    return (
        Task.objects.prefetch_related("tags")
        .select_related("user")
        .get(pk=task.pk)
    )
