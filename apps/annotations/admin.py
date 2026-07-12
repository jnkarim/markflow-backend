from django.contrib import admin

from apps.annotations.models import UploadedImage


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
