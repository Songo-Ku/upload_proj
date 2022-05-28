from rest_framework import serializers
from image.models import UploadedImage, ExpiredLink
from django.core.validators import MaxValueValidator, MinValueValidator



class ExpLinkOnlySerializer(serializers.ModelSerializer):
    link = serializers.ReadOnlyField()

    class Meta:
        model = ExpiredLink
        fields = ['link']


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
    duration = serializers.IntegerField(validators=[MaxValueValidator(30000), MinValueValidator(300)])

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
    date_expire_link = serializers.CharField(source='expired_link.expiry_date')
    expire_link = serializers.ImageField(source='expired_link.link')
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedImage
        fields = ['pk', 'thumbnail_200px', 'thumbnail_400px', 'image',
                  'date_expire_link', 'expire_link', 'photo_url']

    def get_photo_url(self, uploaded_image):
        request = self.context.get('request')
        print('link \n\n', uploaded_image.expired_link.link, 'link \n\n')

        return f'{uploaded_image.expired_link.link}'


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('pk', 'image', 'user', 'thumbnail_200px', 'thumbnail_400px')
        read_only_fields = ['pk']


class ExpLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiredLink
        read_only_fields = ['pk']
        fields = '__all__'














    # def validate_month(self, value):
    #     # print('validuje month')
    #     # print(value)
    #     if MONTHS_NUMBER_DICT.get(str(value)):
    #         return MONTHS_NUMBER_DICT.get(str(value))
    #     else:
    #         raise serializers.ValidationError("Please select month from range 1-12")

    # def validate(self, data):
    #     if MONTHS_DICT.get(data.get('month')):
    #         month_ = MONTHS_DICT.get(data.get('month'))
    #     else:
    #         raise serializers.ValidationError("Please select month from range 1-12")
    #     day_ = int(data.get('day'))
    #     year_ = int(datetime.datetime.today().strftime("%Y"))
    #     try:
    #         datetime.datetime(year_, month_, day_)
    #     except:
    #         raise serializers.ValidationError("Inproperly selected day and month. That date doesnt exist!")
    #     return data

