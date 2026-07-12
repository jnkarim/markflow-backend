from rest_framework import serializers

from apps.annotations.models import UploadedImage


class UploadedImageSerializer(serializers.ModelSerializer):
    """Expose immutable metadata for an uploaded image."""

    class Meta:
        model = UploadedImage
        fields = (
            "id",
            "image",
            "original_name",
            "width",
            "height",
            "file_size",
            "uploaded_at",
            "updated_at",
        )
        read_only_fields = fields
