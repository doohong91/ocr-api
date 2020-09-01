from .models import Image
from rest_framework import serializers


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    # original_img = serializers.ImageField(use_url=True)
    # result_img = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = "__all__"
        read_only_fields = [
            "orig_img",
        ]
