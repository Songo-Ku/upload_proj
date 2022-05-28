import uuid
import os
from datetime import datetime, timedelta
from PIL import Image
from django.db import models
from django.conf import settings
# from rest_framework import viewsets, filters
from django.http import HttpResponse
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
import django.shortcuts
from django.shortcuts import get_object_or_404

from image.serializers import UploadedImageSerializer, ListUploadedImageBasicSerializer, \
    ListUploadedImageEnterpriseSerializer, ListUploadedImagePremiumSerializer, \
    CreateUploadedImageEnterpriseSerializer, CreateUploadedImagePremiumSerializer, \
    CreateUploadedImageBasicSerializer, ExpLinkSerializer
from image.models import UploadedImage, ExpiredLink
from rest_framework import status, mixins, permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from src.settings import BASE_DIR
from .models import create_thumbnail, code_uploaded_filename


# def create_thumbnail(input_image, thumbnail_size=(200, 200)):
#     if not input_image or input_image == "":
#         return None
#     image = Image.open(input_image)
#     image.thumbnail(thumbnail_size, Image.ANTIALIAS)
#     # parse the filename and scramble it
#     filename = code_uploaded_filename(None, os.path.basename(input_image.name))
#     arrdata = filename.split(".")
#     # extension is in the last element, pop it
#     extension = arrdata.pop()
#     basename = "".join(arrdata)
#     # add _thumb to the filename
#     new_filename = basename + "_thumb." + extension
#     # save the image in MEDIA_ROOT and return the filename
#     print('new name \n', new_filename)
#     print('os path join \n', os.path.join(settings.MEDIA_ROOT, new_filename))
#     image.save(os.path.join(settings.MEDIA_ROOT, new_filename))
#     return new_filename


class ModelCustomViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """
    A Customviewset that provides default `create()` and `list()` actions.
    """
    pass


class UploadedImagesViewSet(ModelCustomViewSet):
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.plan == "Premium":
            self.serializer_class = CreateUploadedImagePremiumSerializer
        elif request.user.plan == "Enterprise":
            self.serializer_class = CreateUploadedImageEnterpriseSerializer
        else:
            self.serializer_class = CreateUploadedImageBasicSerializer
        serializer = self.get_serializer(data=request.data)
        print('serializer \n ', serializer, '\n')
        serializer.is_valid(raise_exception=True)
        # print('serializer data before perform create', serializer.data)
        # serializer.data
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

    def list(self, request, *args, **kwargs):
        print('to jest user:\n', request.user, request.user.id, request.user.plan, '\n')
        queryset = UploadedImage.objects.filter(user=request.user.id)
        if request.user.plan == "Premium":
            self.serializer_class = ListUploadedImagePremiumSerializer
        elif request.user.plan == "Enterprise":
            self.serializer_class = ListUploadedImageEnterpriseSerializer
        else:
            self.serializer_class = ListUploadedImageBasicSerializer
        print(self.serializer_class)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class ExpiredLinkImagesViewSet(ModelCustomViewSet):
    queryset = ExpiredLink.objects.all()
    serializer_class = ExpLinkSerializer
    permission_classes = [permissions.IsAuthenticated]


def load_url(request, title):
    print(title)
    exp = ExpiredLink.objects.filter(link=title)
    basedir = BASE_DIR
    print(BASE_DIR, '      \nbase dir')
    print(request)
    print(exp)
    obj_exp_link = get_object_or_404(ExpiredLink, link=title)
    print(obj_exp_link)
    print('obj explink image \n', obj_exp_link.thumbnail.image, '\n')
    context = {
        "basedir": BASE_DIR,
        "exp_link": obj_exp_link
    }
    from django.template import loader
    template = loader.get_template('image/expired_link.html')
    return HttpResponse(template.render(context, request))
    # if exp:
    #     return HttpResponse("link is not exp")
    # url = get_object_or_404(TempUrl, url_hash=hash, expires__gte=datetime.now())
    # data = get_some_data_or_whatever()
    # return render_to_response('some_template.html', {'data':data},
    #                           context_instance=RequestContext(request))
    # return render(
    #     request,
    #     'books/book_detail.html',
    #     {'book': book}
    # )
    # render(request, 'ServeSegments.html', context=context)
    # return HttpResponse("we are handle backend expire link")


