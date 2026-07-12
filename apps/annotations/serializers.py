import re

from rest_framework import serializers

from apps.annotations.models import PolygonAnnotation, UploadedImage

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
MAX_POLYGON_POINTS = 200


class UploadedImageSerializer(serializers.ModelSerializer):
    """Expose immutable image metadata and its saved polygon count."""

    polygon_count = serializers.IntegerField(source="polygons.count", read_only=True)

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
            "polygon_count",
        )
        read_only_fields = fields


class PolygonAnnotationSerializer(serializers.ModelSerializer):
    """Validate and serialize normalized polygon coordinates."""

    class Meta:
        model = PolygonAnnotation
        fields = (
            "id",
            "image",
            "label",
            "color",
            "points",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "image", "created_at", "updated_at")

    def validate_label(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Label cannot be empty.")
        return cleaned

    def validate_color(self, value: str) -> str:
        if not HEX_COLOR_PATTERN.fullmatch(value):
            raise serializers.ValidationError(
                "Color must be a six-digit hexadecimal value such as #FF8A00."
            )
        return value.upper()

    def validate_points(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Points must be a list.")

        if len(value) < 3:
            raise serializers.ValidationError(
                "A polygon requires at least three points."
            )

        if len(value) > MAX_POLYGON_POINTS:
            raise serializers.ValidationError(
                f"A polygon can contain at most {MAX_POLYGON_POINTS} points."
            )

        cleaned_points: list[dict[str, float]] = []

        for index, point in enumerate(value, start=1):
            if not isinstance(point, dict) or "x" not in point or "y" not in point:
                raise serializers.ValidationError(
                    f"Point {index} must contain x and y coordinates."
                )

            if isinstance(point["x"], bool) or isinstance(point["y"], bool):
                raise serializers.ValidationError(
                    f"Point {index} must contain numeric coordinates."
                )

            try:
                x = float(point["x"])
                y = float(point["y"])
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    f"Point {index} must contain numeric coordinates."
                )

            if not 0 <= x <= 1 or not 0 <= y <= 1:
                raise serializers.ValidationError(
                    f"Point {index} must be inside the normalized 0–1 image bounds."
                )

            cleaned_points.append({"x": round(x, 6), "y": round(y, 6)})

        unique_points = {(point["x"], point["y"]) for point in cleaned_points}
        if len(unique_points) < 3:
            raise serializers.ValidationError(
                "A polygon requires at least three distinct points."
            )

        return cleaned_points
