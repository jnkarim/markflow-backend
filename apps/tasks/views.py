from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from apps.tasks.models import Task
from apps.tasks.serializers import TaskReorderSerializer, TaskSerializer
from apps.tasks.services import reorder_task


class TaskViewSet(viewsets.ModelViewSet):
    """Provide user-scoped operations for date-based Kanban tasks."""

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

    @action(detail=False, methods=("post",), url_path="reorder")
    def reorder(self, request):
        """Persist a drag-and-drop move and normalize affected columns."""

        input_serializer = TaskReorderSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            task = reorder_task(
                user=request.user,
                **input_serializer.validated_data,
            )
        except Task.DoesNotExist as exc:
            raise NotFound("Task not found.") from exc

        output_serializer = self.get_serializer(task)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
