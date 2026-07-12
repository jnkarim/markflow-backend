from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("annotations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PolygonAnnotation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(default="Region", max_length=80)),
                ("color", models.CharField(default="#FF8A00", max_length=7)),
                ("points", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polygons",
                        to="annotations.uploadedimage",
                    ),
                ),
            ],
            options={
                "ordering": ("created_at", "id"),
            },
        ),
    ]
