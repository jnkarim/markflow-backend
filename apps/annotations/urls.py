from rest_framework.routers import DefaultRouter

from apps.annotations.views import ImageViewSet

router = DefaultRouter()
router.register("images", ImageViewSet, basename="image")

urlpatterns = router.urls
