from rest_framework import serializers
from image.models import UploadedImage

import uuid
import os

from django.conf import settings
from PIL import Image


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('pk', 'image', 'title', 'user')
        read_only_fields = ['pk']

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

def code_uploaded_filename(instance, filename):
    print(filename, '\n to jest split filename')
    print(filename.split(".")[-1], '\n to ostatni element filename')
    extension = filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4(), extension)


def create_thumbnail(input_image, thumbnail_size=(200, 200)):
    if not input_image or input_image == "":
        return None
    image = Image.open(input_image)
    image.thumbnail(thumbnail_size, Image.ANTIALIAS)
    # parse the filename and scramble it
    filename = code_uploaded_filename(None, os.path.basename(input_image.name))
    arrdata = filename.split(".")
    # extension is in the last element, pop it
    extension = arrdata.pop()
    basename = "".join(arrdata)
    # add _thumb to the filename
    new_filename = basename + "_thumb." + extension
    # save the image in MEDIA_ROOT and return the filename
    print('new name \n', new_filename)
    print('os path join \n', os.path.join(settings.MEDIA_ROOT, new_filename))
    image.save(os.path.join(settings.MEDIA_ROOT, new_filename))
    return new_filename