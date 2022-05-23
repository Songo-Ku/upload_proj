import uuid
import os

from PIL import Image
from django.db import models
from django.conf import settings


# Create your models here.


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
    image = models.ImageField("uploaded image", upload_to=code_uploaded_filename)
    thumbnail = models.ImageField("Thumbnail of the uploaded image", blank=True)
    title = models.CharField(max_length=300, default='unknown')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.thumbnail = create_thumbnail(self.image)
        super(UploadedImage, self).save(force_update=force_update)

    def __str__(self):
        return self.title
