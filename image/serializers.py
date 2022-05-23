from rest_framework import serializers
from image.models import UploadedImage


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('pk', 'image', 'thumbnail', 'title')
        read_only_fields = ['thumbnail', 'pk']