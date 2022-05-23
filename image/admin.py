from django.contrib import admin

# Register your models here.
from image.models import UploadedImage

admin.site.register(UploadedImage)
