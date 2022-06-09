import os
import shutil
import tempfile
from io import StringIO
from io import BytesIO
from pathlib import Path

import PIL
from PIL import Image
# from PIL.Image import Image
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.urls import reverse
from rest_framework import status
from image.models import UploadedImage, ExpiredLink
from rest_framework.test import APITestCase
from user.factories import UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.conf import settings

from user.models import User

FAKE_FILES_TEST_PATH = f'{settings.BASE_DIR}/fake_files/'
UPLOADED_MEDIA_PATH = f'{settings.BASE_DIR}/uploaded_media/'
TEMP_LINKS = f'{settings.BASE_DIR}/temp/'


class ImageListCreateViewSetBasicPlanTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.uploaded_image_list_url = reverse("image:images-list")
        cls.user1 = UserFactory(username="test", plan="Basic")
        cls.images_all = UploadedImage.objects.all()
        cls.images_all.delete()
        cls.simply_upload_test_file = SimpleUploadedFile(
            name='image_test_1.png',
            content=open(f'{FAKE_FILES_TEST_PATH}image_test_1.png', 'rb').read(),
            content_type='image/png'
        )
        super().setUpClass()

    def setUp(self):
        self.client.force_authenticate(user=self.user1)

    def tearDown(self):
        UploadedImage.objects.all().delete()
        if Path(settings.MEDIA_ROOT).is_dir():
            for file_ in os.listdir(Path(settings.MEDIA_ROOT + '/')):
                print(os.listdir(Path(settings.MEDIA_ROOT + '/')))
                os.remove(os.path.join(settings.MEDIA_ROOT, file_))


    # def test_create(self):
    #     # _file = SimpleUploadedFile(self.image, "file_content",
    #     #                            content_type="image/jpeg")
    #     attachment = UploadedImage.objects.create(
    #         image=self.simply_upload_test_file,
    #         user=self.user1,
    #     )
    #     # mock_profile_image = SimpleUploadedFile('f{FAKE_FILES_TEST_PATH}image_test_1.png', get_mock_img(),
    #     #                                         content_type='image/png')
    #
    #     self.assertIsInstance(attachment, UploadedImage)

    def test_mocking(self):
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        valid_image = {
            "image": tmp_file,
        }
        response = self.client.post(
            self.uploaded_image_list_url,
            data=valid_image,
            format="multipart",)