from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.tasks.models import Task


class TaskApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(self.user)

    def test_create_task_with_tags(self):
        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Design annotation toolbar",
                "description": "Prepare the first toolbar iteration.",
                "status": "todo",
                "priority": "high",
                "task_date": "2026-07-12",
                "due_date": "2026-07-13",
                "tag_names": ["Design", "Frontend"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["position"], 0)
        self.assertEqual(len(response.data["tags"]), 2)
        self.assertEqual(Task.objects.get().user, self.user)

    def test_tasks_are_filtered_by_selected_date(self):
        Task.objects.create(
            user=self.user,
            title="Selected day",
            task_date=date(2026, 7, 12),
        )
        Task.objects.create(
            user=self.user,
            title="Different day",
            task_date=date(2026, 7, 13),
        )

        response = self.client.get("/api/tasks/?date=2026-07-12")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Selected day")

    def test_user_cannot_access_another_users_task(self):
        task = Task.objects.create(
            user=self.other_user,
            title="Private task",
            task_date=date(2026, 7, 12),
        )

        response = self.client.get(f"/api/tasks/{task.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_date_filter_returns_clear_error(self):
        response = self.client.get("/api/tasks/?date=not-a-date")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)

    def test_due_date_cannot_be_before_task_date(self):
        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Invalid deadline",
                "task_date": "2026-07-12",
                "due_date": "2026-07-11",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data)


class TaskReorderApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="board-owner@example.com",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            email="other-board@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(self.user)
        self.task_date = date(2026, 7, 12)

    def create_task(self, title, status_value, position, user=None):
        return Task.objects.create(
            user=user or self.user,
            title=title,
            task_date=self.task_date,
            status=status_value,
            position=position,
        )

    def test_move_task_to_another_column_and_compact_source(self):
        first = self.create_task("First", Task.Status.TODO, 0)
        moved = self.create_task("Moved", Task.Status.TODO, 1)
        last = self.create_task("Last", Task.Status.TODO, 2)
        existing_done = self.create_task("Existing done", Task.Status.DONE, 0)

        response = self.client.post(
            "/api/tasks/reorder/",
            {
                "task_id": moved.id,
                "status": Task.Status.DONE,
                "position": 0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Task.Status.DONE)
        self.assertEqual(response.data["position"], 0)

        todo_tasks = list(
            Task.objects.filter(status=Task.Status.TODO).order_by("position")
        )
        done_tasks = list(
            Task.objects.filter(status=Task.Status.DONE).order_by("position")
        )

        self.assertEqual(todo_tasks, [first, last])
        self.assertEqual([task.position for task in todo_tasks], [0, 1])
        self.assertEqual(done_tasks, [moved, existing_done])
        self.assertEqual([task.position for task in done_tasks], [0, 1])

    def test_reorder_task_inside_same_column(self):
        first = self.create_task("First", Task.Status.IN_PROGRESS, 0)
        second = self.create_task("Second", Task.Status.IN_PROGRESS, 1)
        third = self.create_task("Third", Task.Status.IN_PROGRESS, 2)

        response = self.client.post(
            "/api/tasks/reorder/",
            {
                "task_id": third.id,
                "status": Task.Status.IN_PROGRESS,
                "position": 0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ordered = list(
            Task.objects.filter(status=Task.Status.IN_PROGRESS).order_by("position")
        )
        self.assertEqual(ordered, [third, first, second])
        self.assertEqual([task.position for task in ordered], [0, 1, 2])

    def test_position_is_clamped_to_end_of_destination_column(self):
        moved = self.create_task("Moved", Task.Status.TODO, 0)
        existing = self.create_task("Existing", Task.Status.DONE, 0)

        response = self.client.post(
            "/api/tasks/reorder/",
            {
                "task_id": moved.id,
                "status": Task.Status.DONE,
                "position": 999,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        moved.refresh_from_db()
        self.assertEqual(moved.position, 1)
        self.assertEqual(
            list(Task.objects.filter(status=Task.Status.DONE).order_by("position")),
            [existing, moved],
        )

    def test_invalid_reorder_payload_returns_validation_errors(self):
        task = self.create_task("Task", Task.Status.TODO, 0)

        response = self.client.post(
            "/api/tasks/reorder/",
            {"task_id": task.id, "status": "blocked", "position": -1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.assertIn("position", response.data)

    def test_user_cannot_reorder_another_users_task(self):
        private_task = self.create_task(
            "Private",
            Task.Status.TODO,
            0,
            user=self.other_user,
        )

        response = self.client.post(
            "/api/tasks/reorder/",
            {
                "task_id": private_task.id,
                "status": Task.Status.DONE,
                "position": 0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        private_task.refresh_from_db()
        self.assertEqual(private_task.status, Task.Status.TODO)
