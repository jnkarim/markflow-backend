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
