from pathlib import Path

from PIL import Image, UnidentifiedImageError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from apps.annotations.models import UploadedImage
from apps.annotations.serializers import UploadedImageSerializer

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGES_PER_USER = 20


class ImageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """List, upload, retrieve, and delete images owned by the current user."""

    serializer_class = UploadedImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return UploadedImage.objects.filter(user=self.request.user)

    @action(detail=False, methods=("post",), url_path="upload")
    def upload(self, request):
        files = request.FILES.getlist("files")
        if not files:
            return Response(
                {"files": ["Choose at least one image."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_count = self.get_queryset().count()
        if existing_count + len(files) > MAX_IMAGES_PER_USER:
            return Response(
                {
                    "files": [
                        f"Each account can store at most {MAX_IMAGES_PER_USER} images "
                        "in this demo."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        created: list[UploadedImage] = []
        errors: list[str] = []

        for uploaded_file in files:
            error = self._validate_image(uploaded_file)
            if error:
                errors.append(f"{uploaded_file.name}: {error}")
                continue

            width, height = self._read_dimensions(uploaded_file)
            image = UploadedImage.objects.create(
                user=request.user,
                image=uploaded_file,
                original_name=Path(uploaded_file.name).name[:255],
                width=width,
                height=height,
                file_size=uploaded_file.size,
            )
            created.append(image)

        if not created:
            return Response(
                {"files": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(created, many=True)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        if errors:
            response["X-Upload-Warnings"] = " | ".join(errors)
        return response

    def perform_destroy(self, instance):
        storage = instance.image.storage
        stored_name = instance.image.name
        instance.delete()
        if stored_name:
            storage.delete(stored_name)

    @staticmethod
    def _read_dimensions(uploaded_file) -> tuple[int, int]:
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as image:
            width, height = image.size
        uploaded_file.seek(0)
        return width, height

    @staticmethod
    def _validate_image(uploaded_file) -> str | None:
        if uploaded_file.size > MAX_IMAGE_SIZE:
            return "file is larger than 5 MB."

        if uploaded_file.content_type not in ALLOWED_IMAGE_TYPES:
            return "unsupported format. Use JPG, PNG, or WEBP."

        try:
            uploaded_file.seek(0)
            with Image.open(uploaded_file) as image:
                image.verify()
            uploaded_file.seek(0)
        except (UnidentifiedImageError, OSError, SyntaxError):
            return "the file is not a valid image."

        return None
