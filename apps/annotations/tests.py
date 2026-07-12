from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.annotations.models import PolygonAnnotation, UploadedImage


def make_image_file(name: str = "sample.png", image_format: str = "PNG"):
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
        {"x": 0.1, "y": 0.15},
        {"x": 0.8, "y": 0.2},
        {"x": 0.55, "y": 0.85},
    ]


class ImageUploadApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="image-owner@example.com",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            email="other-image-owner@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(self.user)
        self.media_directory = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(self.media_directory.cleanup)

    def test_uploads_multiple_valid_images(self):
        response = self.client.post(
            "/api/images/upload/",
            {
                "files": [
                    make_image_file("first.png"),
                    make_image_file("second.png"),
                ]
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(UploadedImage.objects.filter(user=self.user).count(), 2)
        self.assertEqual(response.data[0]["width"], 32)
        self.assertEqual(response.data[0]["height"], 24)
        self.assertEqual(response.data[0]["polygon_count"], 0)

    def test_uploaded_images_are_isolated_by_user(self):
        UploadedImage.objects.create(
            user=self.other_user,
            image="uploads/user_other/private.png",
            original_name="private.png",
            width=10,
            height=10,
            file_size=100,
        )
        UploadedImage.objects.create(
            user=self.user,
            image="uploads/user_owner/owned.png",
            original_name="owned.png",
            width=10,
            height=10,
            file_size=100,
        )

        response = self.client.get("/api/images/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["original_name"], "owned.png")

    def test_rejects_an_unsupported_file(self):
        response = self.client.post(
            "/api/images/upload/",
            {
                "files": SimpleUploadedFile(
                    "notes.txt",
                    b"not an image",
                    content_type="text/plain",
                )
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("files", response.data)
        self.assertEqual(UploadedImage.objects.count(), 0)

    def test_rejects_a_corrupted_file_with_an_image_content_type(self):
        response = self.client.post(
            "/api/images/upload/",
            {
                "files": SimpleUploadedFile(
                    "broken.png",
                    b"this is not a real png",
                    content_type="image/png",
                )
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UploadedImage.objects.count(), 0)

    def test_user_cannot_delete_another_users_image(self):
        private_image = UploadedImage.objects.create(
            user=self.other_user,
            image="uploads/user_other/private.png",
            original_name="private.png",
            width=10,
            height=10,
            file_size=100,
        )

        response = self.client.delete(f"/api/images/{private_image.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(UploadedImage.objects.filter(id=private_image.id).exists())


class PolygonAnnotationApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="polygon-owner@example.com",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            email="other-polygon-owner@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(self.user)
        self.image = UploadedImage.objects.create(
            user=self.user,
            image="uploads/user_owner/image.png",
            original_name="image.png",
            width=1000,
            height=800,
            file_size=2000,
        )
        self.other_image = UploadedImage.objects.create(
            user=self.other_user,
            image="uploads/user_other/private.png",
            original_name="private.png",
            width=1000,
            height=800,
            file_size=2000,
        )

    def test_creates_and_lists_a_normalized_polygon(self):
        create_response = self.client.post(
            f"/api/images/{self.image.id}/polygons/",
            {
                "label": "Product",
                "color": "#ff8a00",
                "points": valid_points(),
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["label"], "Product")
        self.assertEqual(create_response.data["color"], "#FF8A00")
        self.assertEqual(create_response.data["image"], self.image.id)

        list_response = self.client.get(
            f"/api/images/{self.image.id}/polygons/"
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["points"], valid_points())

    def test_image_response_includes_polygon_count(self):
        PolygonAnnotation.objects.create(
            image=self.image,
            label="Region",
            color="#FF8A00",
            points=valid_points(),
        )

        response = self.client.get(f"/api/images/{self.image.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["polygon_count"], 1)

    def test_rejects_polygon_with_fewer_than_three_points(self):
        response = self.client.post(
            f"/api/images/{self.image.id}/polygons/",
            {
                "label": "Invalid",
                "color": "#FF8A00",
                "points": valid_points()[:2],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("points", response.data)

    def test_rejects_polygon_outside_normalized_bounds(self):
        points = valid_points()
        points[1] = {"x": 1.2, "y": 0.4}

        response = self.client.post(
            f"/api/images/{self.image.id}/polygons/",
            {
                "label": "Invalid",
                "color": "#FF8A00",
                "points": points,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("points", response.data)

    def test_rejects_invalid_polygon_color(self):
        response = self.client.post(
            f"/api/images/{self.image.id}/polygons/",
            {
                "label": "Invalid",
                "color": "orange",
                "points": valid_points(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("color", response.data)

    def test_user_cannot_create_polygon_on_another_users_image(self):
        response = self.client.post(
            f"/api/images/{self.other_image.id}/polygons/",
            {
                "label": "Private",
                "color": "#FF8A00",
                "points": valid_points(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(PolygonAnnotation.objects.count(), 0)

    def test_user_can_update_own_polygon(self):
        polygon = PolygonAnnotation.objects.create(
            image=self.image,
            label="Old label",
            color="#FF8A00",
            points=valid_points(),
        )

        response = self.client.patch(
            f"/api/polygons/{polygon.id}/",
            {"label": "Updated label", "color": "#22C982"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        polygon.refresh_from_db()
        self.assertEqual(polygon.label, "Updated label")
        self.assertEqual(polygon.color, "#22C982")

    def test_user_can_delete_own_polygon(self):
        polygon = PolygonAnnotation.objects.create(
            image=self.image,
            label="Delete me",
            color="#FF8A00",
            points=valid_points(),
        )

        response = self.client.delete(f"/api/polygons/{polygon.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PolygonAnnotation.objects.filter(id=polygon.id).exists())

    def test_user_cannot_delete_another_users_polygon(self):
        polygon = PolygonAnnotation.objects.create(
            image=self.other_image,
            label="Private",
            color="#FF8A00",
            points=valid_points(),
        )

        response = self.client.delete(f"/api/polygons/{polygon.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PolygonAnnotation.objects.filter(id=polygon.id).exists())
