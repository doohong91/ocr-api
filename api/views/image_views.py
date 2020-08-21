from rest_framework.viewsets import ModelViewSet
from api.models import Image
from api.serializers import ImageSerializer


class ImageViewSet(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
