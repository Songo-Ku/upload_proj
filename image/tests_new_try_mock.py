import os
import tempfile
from pathlib import Path
from PIL import Image
from django.core.files import File
from django.urls import reverse
from image.models import UploadedImage
from rest_framework.test import APITestCase
from user.factories import UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

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
                os.remove(os.path.join(settings.MEDIA_ROOT, file_))

    def test_save_image_to_db_basic(self):
        image = UploadedImage.objects.create(
            image=self.simply_upload_test_file,
            user=self.user1,
        )
        self.assertIsInstance(image, UploadedImage)

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