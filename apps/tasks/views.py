from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """Provide user-scoped CRUD operations for date-based tasks."""

    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = (
            Task.objects.filter(user=self.request.user)
            .prefetch_related("tags")
            .order_by("status", "position", "created_at")
        )

        selected_date = self.request.query_params.get("date")
        if selected_date:
            parsed_date = parse_date(selected_date)
            if parsed_date is None:
                raise ValidationError(
                    {"date": "Enter a valid date in YYYY-MM-DD format."}
                )
            queryset = queryset.filter(task_date=parsed_date)

        return queryset

    def perform_create(self, serializer):
        task_date = serializer.validated_data["task_date"]
        task_status = serializer.validated_data.get("status", Task.Status.TODO)
        next_position = Task.objects.filter(
            user=self.request.user,
            task_date=task_date,
            status=task_status,
        ).count()
        serializer.save(position=next_position)
