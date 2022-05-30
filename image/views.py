from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template import loader

from image.serializers import UploadedImageSerializer, ListUploadedImageBasicSerializer, \
    ListUploadedImageEnterpriseSerializer, ListUploadedImagePremiumSerializer, \
    CreateUploadedImageEnterpriseSerializer, CreateUploadedImagePremiumSerializer, \
    CreateUploadedImageBasicSerializer
from image.models import UploadedImage, ExpiredLink
from rest_framework import status, mixins, permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django.conf import settings


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
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

    def list(self, request, *args, **kwargs):
        queryset = UploadedImage.objects.filter(user=request.user.id)
        if request.user.plan == "Premium":
            self.serializer_class = ListUploadedImagePremiumSerializer
        elif request.user.plan == "Enterprise":
            self.serializer_class = ListUploadedImageEnterpriseSerializer
        else:
            self.serializer_class = ListUploadedImageBasicSerializer
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def load_url(request, title):
    obj_exp_link = get_object_or_404(ExpiredLink, link=title)
    context = {
        "info_error": 'this link is expired'
    }
    if obj_exp_link.is_expired == True:
        template = loader.get_template(f'{settings.BASE_DIR}/templates/image/expired_link.html')
        return HttpResponseNotFound(template.render(context, request), status=status.HTTP_404_NOT_FOUND)
    return redirect(f'/temp/{title}')

