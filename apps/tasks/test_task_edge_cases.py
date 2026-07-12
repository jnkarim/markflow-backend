from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.tasks.models import Tag, Task


class TaskEdgeCaseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="task-edge@example.com",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            email="task-edge-other@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(self.user)

    def test_task_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/tasks/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_whitespace_only_title_is_rejected(self):
        response = self.client.post(
            "/api/tasks/",
            {"title": "   ", "task_date": "2026-07-12"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_duplicate_tag_names_are_deduplicated_case_insensitively(self):
        response = self.client.post(
            "/api/tasks/",
            {
                "title": "Prepare UI audit",
                "task_date": "2026-07-12",
                "tag_names": ["Design", " design ", "DESIGN"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["tags"]), 1)
        self.assertEqual(Tag.objects.filter(user=self.user).count(), 1)

    def test_positions_increment_per_date_and_status_column(self):
        first_todo = self.client.post(
            "/api/tasks/",
            {"title": "First", "task_date": "2026-07-12", "status": "todo"},
            format="json",
        )
        second_todo = self.client.post(
            "/api/tasks/",
            {"title": "Second", "task_date": "2026-07-12", "status": "todo"},
            format="json",
        )
        first_done = self.client.post(
            "/api/tasks/",
            {"title": "Done", "task_date": "2026-07-12", "status": "done"},
            format="json",
        )
        next_day = self.client.post(
            "/api/tasks/",
            {"title": "Tomorrow", "task_date": "2026-07-13", "status": "todo"},
            format="json",
        )

        self.assertEqual(first_todo.data["position"], 0)
        self.assertEqual(second_todo.data["position"], 1)
        self.assertEqual(first_done.data["position"], 0)
        self.assertEqual(next_day.data["position"], 0)

    def test_partial_update_validates_due_date_against_existing_task_date(self):
        task = Task.objects.create(
            user=self.user,
            title="Existing task",
            task_date=date(2026, 7, 12),
        )

        response = self.client.patch(
            f"/api/tasks/{task.id}/",
            {"due_date": "2026-07-11"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data)

    def test_user_cannot_delete_another_users_task(self):
        private_task = Task.objects.create(
            user=self.other_user,
            title="Private task",
            task_date=date(2026, 7, 12),
        )

        response = self.client.delete(f"/api/tasks/{private_task.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(id=private_task.id).exists())
