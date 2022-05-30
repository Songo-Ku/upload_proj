from django.contrib import admin
from image.models import UploadedImage, ExpiredLink

admin.site.register(UploadedImage)
admin.site.register(ExpiredLink)



