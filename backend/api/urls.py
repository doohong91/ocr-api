from django.conf import settings
from django.urls import path, include, re_path

from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.views import image_views

# # Viewset의 methods를 자동으로 Routing
# router = DefaultRouter()
# router.register("image", image_views.ImageViewSet)

# swagger 정보 설정
schema_view = get_schema_view(
    openapi.Info(
        title="OCR API",
        default_version="v0.1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path("", include(router.urls)),
    path("post/", image_views.ImageView.as_view()),
]

# swagger관련 End Point 추가 (DEBUG Mode에서만 노출)
if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        re_path(
            r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"
        ),
        re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]
