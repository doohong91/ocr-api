from .models import Image
from rest_framework import serializers


class ImageUploadSerializer(serializers.HyperlinkedModelSerializer):
    original_img = serializers.ImageField(use_url=True)
    result_img = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = [
            "original_img",
            "result_img",
            "bounding_boxes",
        ]

