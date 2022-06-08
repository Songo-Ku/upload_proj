from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from image import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('image.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('temp/<uuid:uuid>/', views.TempView.as_view(), name='url_link'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




