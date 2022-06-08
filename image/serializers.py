from rest_framework import serializers
from image.models import UploadedImage, ExpiredLink
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings


class CreateUploadedImageBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('pk', 'image', 'thumbnail_200px')
        read_only_fields = ['pk', 'thumbnail_200px']


class CreateUploadedImagePremiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('pk', 'image', 'user', 'thumbnail_200px', 'thumbnail_400px')
        read_only_fields = ['pk', 'thumbnail_200px', 'thumbnail_400px']


class CreateUploadedImageEnterpriseSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField(
        validators=[
            MaxValueValidator(30000),
            MinValueValidator(300)
        ],
        required=False
    )

    class Meta:
        model = UploadedImage
        fields = ('pk', 'image', 'duration')
        read_only_fields = ['pk']


class ListUploadedImageBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ['image', 'thumbnail_200px']


class ListUploadedImagePremiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ['image', 'thumbnail_200px', 'thumbnail_400px']


class ListUploadedImageEnterpriseSerializer(serializers.ModelSerializer):
    date_expire_link = serializers.CharField(source='expired_link.expiry_date', allow_null=True)
    expire_link = serializers.SerializerMethodField()

    class Meta:
        model = UploadedImage
        fields = ['pk', 'thumbnail_200px', 'thumbnail_400px', 'image',
                  'expire_link', 'date_expire_link']

    def get_expire_link(self, uploaded_image):
        try:
            uuid = uploaded_image.expired_link.uuid
            return f'{settings.DOMAIN_URL}temp/{uuid}/'
        except:
            return 'No Expire link added'


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('pk', 'image', 'user', 'thumbnail_200px', 'thumbnail_400px')
        read_only_fields = ['pk']



