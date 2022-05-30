from rest_framework import routers
from image.views import UploadedImagesViewSet

app_name = 'image'
router = routers.DefaultRouter()
router.register('images', UploadedImagesViewSet, basename='images')
urlpatterns = []
urlpatterns += router.urls