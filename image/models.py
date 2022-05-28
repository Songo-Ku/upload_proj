# validation links for file
# https://docs.djangoproject.com/en/2.2/_modules/django/core/validators/#validate_image_file_extension
# https://stackoverflow.com/questions/20761092/how-to-validate-image-format-in-django-imagefield

import uuid
import os
from datetime import datetime, timedelta
from PIL import Image
from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator

from image.utils import code_uploaded_filename, create_thumbnail, create_image
from user.models import User


class UploadedImage(models.Model):
    image = models.ImageField(
        "uploaded image",
        upload_to=code_uploaded_filename,
        validators=[FileExtensionValidator(['jpg', 'png'])]
    )
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    thumbnail_200px = models.ImageField("Thumbnail of uploaded image 200 px", blank=True)
    thumbnail_400px = models.ImageField("Thumbnail of uploaded image 400 px", blank=True)
    duration = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        print('to jest user w save dla models\n', self.user, '\n')
        self.thumbnail_200px = create_thumbnail(self.image, height_px=200)
        if self.user.plan == 'Premium' or self.user.plan == 'Enterprise':
            self.thumbnail_400px = create_thumbnail(self.image, height_px=400)

        super(UploadedImage, self).save(force_update=force_update)
        if self.user.plan == 'Enterprise' and self.duration:
            expiry_date = datetime.now() + timedelta(seconds=self.duration)
            uploaded_image = UploadedImage.objects.get(pk=self.pk)
            link = create_image(self.image, path_to_upload=settings.TEMP_ROOT)
            print(link)
            exp_link = ExpiredLink(thumbnail=uploaded_image, expiry_date=expiry_date, link=link)
            exp_link.save()

    def show_exp_link(self):
        return self.expired_link.link

    def __str__(self):
        return f' zdjecie o pk {self.pk}'


class ExpiredLink(models.Model):
    thumbnail = models.OneToOneField(UploadedImage, on_delete=models.CASCADE, related_name='expired_link',
                                     blank=True, null=True)
    expiry_date = models.DateTimeField()
    link = models.ImageField(blank=True, upload_to='temp')  # , upload_to=code_uploaded_filename

    @property
    def is_expired(self):
        return datetime.now() > self.expiry_date

    def __str__(self):
        return f'link dla image: {self.thumbnail.pk}'




















    # title = models.CharField(max_length=300, default='unknown')














# class TempUrl(models.Model):
#     images = models.ForeignKey(UploadedImage, on_delete=models.CASCADE, related_name='images')
#     url_hash = models.CharField("Url", blank=False, max_length=32, unique=True)
#     duration = models.PositiveIntegerField(validators=[MaxValueValidator(30000), MinValueValidator(300)], null=True)
#     expired = models.DateTimeField("Expires", blank=True)
#
#     @property
#     def is_expired(self):
#         if datetime.now > self.expiry_date:
#             return True
#         return False
#
#     def set_expired_date(self):
#         # jesli self.expires bedzie obiektem typu datetime zapisanym jako dzien i czas to zadzialaja te operacje
#         # datetime.now() + timedelta(seconds=300)
#         self.expired = self.created + timedelta(seconds=self.duration)




