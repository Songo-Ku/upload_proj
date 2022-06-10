import os
from django.urls import reverse
from rest_framework import status
from image.models import UploadedImage, ExpiredLink
from rest_framework.test import APITestCase
from user.factories import UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from pathlib import Path
from .fakes import read_fake_image_png_to_post, create_fake_image_jpg_to_post

FAKE_FILES_TEST_PATH = f'{settings.BASE_DIR}/fake_files/'
UPLOADED_MEDIA_PATH = f'{settings.BASE_DIR}/uploaded_media/'
TEMP_LINKS = f'{settings.BASE_DIR}/temp/'


class ImageListCreateViewSetBasicPlanTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.uploaded_image_list_url = reverse("image:images-list")
        cls.user_basic = UserFactory(plan="Basic")
        cls.images_all = UploadedImage.objects.all()
        cls.images_all.delete()
        super().setUpClass()

    def setUp(self):
        self.simply_upload_test_file = SimpleUploadedFile(
            name='image_test_1.png',
            content=open(f'{FAKE_FILES_TEST_PATH}image_test_1.png', 'rb').read(),
            content_type='image/png'
        )
        self.client.force_authenticate(user=self.user_basic)

    def tearDown(self):
        UploadedImage.objects.all().delete()
        if Path(settings.MEDIA_ROOT).is_dir():
            for file_ in os.listdir(Path(settings.MEDIA_ROOT + '/')):
                os.remove(os.path.join(settings.MEDIA_ROOT, file_))

    def test_delete_all_uploaded_images_fetch_empty_list(self):
        response1 = self.client.get(self.uploaded_image_list_url)
        self.assertEquals([], response1.data)

    def test_multiple_variants_with_post_image_basic(self):
        valid_image = {
            "image": self.simply_upload_test_file,
        }
        response = self.client.post(
            self.uploaded_image_list_url,
            data=valid_image,
            format="multipart",)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        file_name_test = str(response.data.get("image").split("/")[-1])
        self.assertEquals(True, os.path.isfile(f'{settings.BASE_DIR}/uploaded_media/{file_name_test}'))
        qs_test_all = UploadedImage.objects.all()
        image_test = UploadedImage.objects.get(pk=response.data.get("pk"))
        self.assertIn(image_test, qs_test_all)
        self.assertEquals(response.data.get('thumbnail_400px', False), False)
        self.assertEquals(response.data.get('duration', False), False)

    def test_define_not_permited_field_duration_basic_tier(self):
        valid_image = {
            "image": self.simply_upload_test_file,
            "duration": 3000
        }
        response = self.client.post(
            self.uploaded_image_list_url,
            data=valid_image,
            format="multipart",)
        self.assertEquals("no exist", response.data.get("duration", "no exist"))
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data.get('thumbnail_400px', False), False)

    def test_added_obj_manually_to_db(self):
        new_uploaded_image = UploadedImage(
            user=self.user_basic,
            image=read_fake_image_png_to_post(),
        )
        new_uploaded_image.save()
        response1 = self.client.get(self.uploaded_image_list_url)
        self.assertEquals(response1.data[0].get("thumbnail_400px", 'not exist'), 'not exist')
        self.assertEquals(response1.data[0].get("duration", 'not exist'), 'not exist')
        self.assertEquals(1, len(response1.data))
        qs_test_all = UploadedImage.objects.all()
        self.assertIn(new_uploaded_image, qs_test_all)

    def test_str_input_as_image_plan_basic(self):
        before_create_image_objects_in_db = UploadedImage.objects.count()
        valid_image = {
            "image": 'some string',
        }
        response = self.client.post(
            self.uploaded_image_list_url,
            data=valid_image,
            format="multipart",)
        self.assertEquals(before_create_image_objects_in_db, UploadedImage.objects.count())
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def create_3_diff_images_to_db_basic_plan(self):
        list_of_images = ['image_test_1.png', 'image_test_2.png', 'image_test_3.jpg']
        for name_file in list_of_images:
            new_uploaded_image = UploadedImage(user=self.user_basic)
            new_uploaded_image.image = read_fake_image_png_to_post(image_from_fakes=name_file)
            new_uploaded_image.save()

    def test_list_records_return_proper_fields(self):
        self.create_3_diff_images_to_db_basic_plan()
        response = self.client.get(self.uploaded_image_list_url)
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(3, len(response.data))
        self.assertEquals(response.data[0].get("image").split('.')[-1], 'png')
        self.assertEquals(response.data[2].get("image").split('.')[-1], 'jpg')
        self.assertIn('thum', response.data[1].get("thumbnail_200px").split('/')[-1])
        self.assertEquals(UploadedImage.objects.count(), len(response.data))

