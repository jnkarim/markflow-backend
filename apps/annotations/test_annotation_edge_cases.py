from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.annotations.models import PolygonAnnotation, UploadedImage


def make_image_file(name="sample.png", image_format="PNG"):
    buffer = BytesIO()
    Image.new("RGB", (32, 24), color=(255, 138, 0)).save(
        buffer,
        format=image_format,
    )
    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type=f"image/{image_format.lower()}",
    )


def valid_points():
    return [
        {"x": 0.1, "y": 0.1},
        {"x": 0.9, "y": 0.1},
        {"x": 0.5, "y": 0.9},
    ]


class AnnotationEdgeCaseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="annotation-edge@example.com",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            email="annotation-edge-other@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(self.user)
        self.media_directory = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(self.media_directory.cleanup)

    def create_image(self, *, user=None, name="stored.png"):
        return UploadedImage.objects.create(
            user=user or self.user,
            image=f"uploads/{name}",
            original_name=name,
            width=32,
            height=24,
            file_size=100,
        )

    def test_image_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/images/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_requires_at_least_one_file(self):
        response = self.client.post("/api/images/upload/", {}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("files", response.data)

    def test_rejects_image_larger_than_five_megabytes(self):
        oversized = SimpleUploadedFile(
            "oversized.png",
            b"x" * (5 * 1024 * 1024 + 1),
            content_type="image/png",
        )

        response = self.client.post(
            "/api/images/upload/",
            {"files": oversized},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("larger than 5 MB", response.data["files"][0])

    def test_account_cannot_store_more_than_twenty_images(self):
        for index in range(20):
            self.create_image(name=f"existing-{index}.png")

        response = self.client.post(
            "/api/images/upload/",
            {"files": make_image_file()},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("at most 20 images", response.data["files"][0])

    def test_partial_upload_returns_valid_files_and_warning_header(self):
        response = self.client.post(
            "/api/images/upload/",
            {
                "files": [
                    make_image_file("valid.png"),
                    SimpleUploadedFile(
                        "invalid.txt",
                        b"not an image",
                        content_type="text/plain",
                    ),
                ]
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)
        self.assertIn("X-Upload-Warnings", response.headers)
        self.assertIn("invalid.txt", response.headers["X-Upload-Warnings"])

    def test_deleting_image_removes_database_record_and_stored_file(self):
        upload_response = self.client.post(
            "/api/images/upload/",
            {"files": make_image_file("delete-me.png")},
            format="multipart",
        )
        image = UploadedImage.objects.get(id=upload_response.data[0]["id"])
        stored_path = Path(image.image.path)
        self.assertTrue(stored_path.exists())

        response = self.client.delete(f"/api/images/{image.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UploadedImage.objects.filter(id=image.id).exists())
        self.assertFalse(stored_path.exists())

    def test_rejects_polygon_without_three_distinct_points(self):
        image = self.create_image()
        points = [
            {"x": 0.1, "y": 0.1},
            {"x": 0.1, "y": 0.1},
            {"x": 0.8, "y": 0.8},
        ]

        response = self.client.post(
            f"/api/images/{image.id}/polygons/",
            {"label": "Invalid", "color": "#FF8A00", "points": points},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("points", response.data)

    def test_rejects_polygon_with_more_than_two_hundred_points(self):
        image = self.create_image()
        points = [
            {"x": index / 200, "y": (index % 10) / 10}
            for index in range(201)
        ]

        response = self.client.post(
            f"/api/images/{image.id}/polygons/",
            {"label": "Too detailed", "color": "#FF8A00", "points": points},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("points", response.data)

    def test_deleting_image_cascades_its_polygons(self):
        image = self.create_image()
        polygon = PolygonAnnotation.objects.create(
            image=image,
            label="Region",
            color="#FF8A00",
            points=valid_points(),
        )

        response = self.client.delete(f"/api/images/{image.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PolygonAnnotation.objects.filter(id=polygon.id).exists())

    def test_user_cannot_retrieve_another_users_polygon(self):
        image = self.create_image(user=self.other_user, name="private.png")
        polygon = PolygonAnnotation.objects.create(
            image=image,
            label="Private",
            color="#FF8A00",
            points=valid_points(),
        )

        response = self.client.get(f"/api/polygons/{polygon.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
