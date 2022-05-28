from rest_framework import routers
from django.urls import path, include

from image.views import UploadedImagesViewSet, ExpiredLinkImagesViewSet

app_name = 'image'
router = routers.DefaultRouter()
router.register('images', UploadedImagesViewSet, basename='images')
router.register('links', ExpiredLinkImagesViewSet, basename='links')


urlpatterns = []
urlpatterns += router.urls