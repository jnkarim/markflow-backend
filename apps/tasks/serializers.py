from rest_framework import serializers

from apps.tasks.models import Tag, Task


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color")
        read_only_fields = ("id",)


class TaskSerializer(serializers.ModelSerializer):
    """Serialize tasks while accepting simple tag names from the client."""

    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=40),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "priority",
            "task_date",
            "due_date",
            "position",
            "tags",
            "tag_names",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "position", "created_at", "updated_at")

    def validate_title(self, value: str) -> str:
        title = value.strip()
        if not title:
            raise serializers.ValidationError("Title cannot be blank.")
        return title

    def validate(self, attrs):
        task_date = attrs.get("task_date", getattr(self.instance, "task_date", None))
        due_date = attrs.get("due_date", getattr(self.instance, "due_date", None))

        if task_date and due_date and due_date < task_date:
            raise serializers.ValidationError(
                {"due_date": "Due date cannot be before the task date."}
            )
        return attrs

    def _set_tags(self, task: Task, names: list[str]) -> None:
        user = self.context["request"].user
        tags: list[Tag] = []
        seen: set[str] = set()

        for raw_name in names:
            name = raw_name.strip()
            normalized = name.casefold()
            if not name or normalized in seen:
                continue

            tag = Tag.objects.filter(user=user, name__iexact=name).first()
            if tag is None:
                tag = Tag.objects.create(user=user, name=name)

            tags.append(tag)
            seen.add(normalized)

        task.tags.set(tags)

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        task = Task.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )
        self._set_tags(task, tag_names)
        return task

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)
        task = super().update(instance, validated_data)
        if tag_names is not None:
            self._set_tags(task, tag_names)
        return task
