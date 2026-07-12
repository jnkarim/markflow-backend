from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models


def uploaded_image_path(instance: "UploadedImage", filename: str) -> str:
    """Store each upload under its owner with a collision-safe filename."""

    suffix = Path(filename).suffix.lower()
    return f"uploads/user_{instance.user_id}/{uuid4().hex}{suffix}"


class UploadedImage(models.Model):
    """An image owned by one user and available for later annotation."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_images",
    )
    image = models.ImageField(upload_to=uploaded_image_path)
    original_name = models.CharField(max_length=255)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    file_size = models.PositiveBigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-uploaded_at", "-id")

    def __str__(self) -> str:
        return self.original_name
