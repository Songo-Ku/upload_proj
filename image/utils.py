import uuid
import os
from PIL import Image
from django.conf import settings


def rescale_px_image(width_original, height_original, height_px=200):
    # return tuple with width and height after rescale
    return (height_px * width_original / height_original, height_px)


def code_uploaded_filename(instance, filename):
    print(filename, '\n to jest filename')
    print(filename.split(".")[-1], '\n to ostatni element po split filename')
    extension = filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4(), extension)


def create_thumbnail(input_image, height_px=200, path_to_upload=settings.MEDIA_ROOT):
    if not input_image or input_image == "":
        return None
    image = Image.open(input_image)
    image.thumbnail(rescale_px_image(image.width, image.height, height_px=height_px), Image.ANTIALIAS)
    # parse the filename and scramble it
    filename = code_uploaded_filename(None, os.path.basename(input_image.name))
    arrdata = filename.split(".")
    # extension is in the last element, pop it
    extension = arrdata.pop()
    basename = "".join(arrdata)
    # add _thumb to the filename
    # print('to jest base name\n', basename)
    new_filename = basename + "_thumb." + extension
    # save the image in MEDIA_ROOT and return the filename
    # print('new name \n', new_filename)
    # print('os path join \n', os.path.join(settings.MEDIA_ROOT, new_filename))
    image.save(os.path.join(path_to_upload, new_filename))
    return new_filename


def create_image(input_image, path_to_upload=settings.TEMP_ROOT):
    if not input_image or input_image == "":
        return None
    image = Image.open(input_image)
    image.thumbnail((image.width, image.height), Image.ANTIALIAS)
    # parse the filename and scramble it
    filename = code_uploaded_filename(None, os.path.basename(input_image.name))
    arrdata = filename.split(".")
    # extension is in the last element, pop it
    extension = arrdata.pop()
    basename = "".join(arrdata)
    print('to jest base name\n', basename)
    # add _thumb to the filename
    new_filename = basename + "_expire_link." + extension
    # save the image in MEDIA_ROOT and return the filename
    print('new name \n', new_filename)
    print('os path join \n', os.path.join(path_to_upload, new_filename))
    image.save(os.path.join(path_to_upload, new_filename))
    return new_filename



