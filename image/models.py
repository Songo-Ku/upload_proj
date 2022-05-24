import uuid
import os
from datetime import datetime, timedelta

from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
# validation links for file
# https://docs.djangoproject.com/en/2.2/_modules/django/core/validators/#validate_image_file_extension
# https://stackoverflow.com/questions/20761092/how-to-validate-image-format-in-django-imagefield
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator


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


class UploadedImage(models.Model):
    image = models.ImageField("uploaded image", upload_to=code_uploaded_filename,
                              validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])])
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=300, default='unknown')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # self.thumbnail = create_thumbnail(self.image)
        super(UploadedImage, self).save(force_update=force_update)

    def __str__(self):
        return self.title


# class ExpireTime(models.Model):
#     number = models.IntegerField(validators=[MaxValueValidator(30000), MinValueValidator(300)])


class TempUrl(models.Model):
    images = models.ForeignKey(UploadedImage, on_delete=models.CASCADE, related_name='images')
    url_hash = models.CharField("Url", blank=False, max_length=32, unique=True)
    duration = models.PositiveIntegerField(validators=[MaxValueValidator(30000), MinValueValidator(300)])
    expired = models.DateTimeField("Expires", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        if datetime.now > self.expiry_date:
            return True
        return False

    def set_expired_date(self):
        # jesli self.expires bedzie obiektem typu datetime zapisanym jako dzien i czas to zadzialaja te operacje
        # datetime.now() + timedelta(seconds=300)
        self.expired = self.created + timedelta(seconds=self.duration)
