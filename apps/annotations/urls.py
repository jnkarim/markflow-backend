from rest_framework.routers import DefaultRouter

from apps.annotations.views import ImageViewSet, PolygonAnnotationViewSet

router = DefaultRouter()
router.register("images", ImageViewSet, basename="image")
router.register("polygons", PolygonAnnotationViewSet, basename="polygon")

urlpatterns = router.urls
