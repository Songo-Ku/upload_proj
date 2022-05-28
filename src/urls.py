from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from image import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('image.urls')),
    # path('auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # path(r'media/(?P<hash>\w+)/$', views.load_url, name='url')
    # re_path(r'^media/(?P<slug>[\w-]+)/$', views.load_url),
    path('temp/<str:title>/', views.load_url, name='url_link'),

]
# urlpatterns = patterns('', url(r'^media/(?P<hash>\w+)/$', 'your.views.load_url', name="url"), )
# urlpatterns =+ path(r'media/(?P<hash>\w+)/$', 'your.views.load_url', name="url")
# path('<int:id>/update-book/', views.BookUpdateView.as_view(), name='book_update'),
# (?P<slug>[\w-]+)/$'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.TEMP_URL, document_root=settings.TEMP_ROOT)


# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)






