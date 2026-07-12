from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.annotations.models import UploadedImage


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
