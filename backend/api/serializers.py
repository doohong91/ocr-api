from .models import Image
from rest_framework import serializers


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    img = serializers.ImageField(use_url=True)
    # image = serializers.ImageField()

    class Meta:
        model = Image
        fields = "__all__"
