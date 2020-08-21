from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import image_views

router = DefaultRouter()
router.register("ocr", image_views.ImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
