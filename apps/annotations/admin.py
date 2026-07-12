from django.contrib import admin

from apps.annotations.models import PolygonAnnotation, UploadedImage


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = (
        "original_name",
        "user",
        "width",
        "height",
        "file_size",
        "uploaded_at",
    )
    list_filter = ("uploaded_at",)
    search_fields = ("original_name", "user__email")
    readonly_fields = (
        "width",
        "height",
        "file_size",
        "uploaded_at",
        "updated_at",
    )


@admin.register(PolygonAnnotation)
class PolygonAnnotationAdmin(admin.ModelAdmin):
    list_display = ("label", "image", "color", "created_at")
    list_filter = ("created_at", "color")
    search_fields = ("label", "image__original_name", "image__user__email")
    readonly_fields = ("created_at", "updated_at")
