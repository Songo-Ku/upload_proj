import os
from django.urls import reverse
from rest_framework import status
from image.models import UploadedImage, ExpiredLink
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
        cls.user1 = UserFactory(plan="Basic")
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
        image_test = UploadedImage.objects.get(pk=response.data.get("pk"))
        check_is_duration_in_request = response.data.get("duration", "duration not defined")
        self.assertEquals('duration not defined', check_is_duration_in_request)
        qs_test_all = UploadedImage.objects.all()
        self.assertIn(image_test, qs_test_all)
        try:
            os.remove(f'{settings.BASE_DIR}/uploaded_media/{file_name_test}')
            os.remove(f'{UPLOADED_MEDIA_PATH}{image_test.thumbnail_200px}')
        except:
            print('nie moge usunac zdjecia wgranego podczas testow, mozna dac aplikacje z logami i to uchwycic')
        if image_test.thumbnail_400px == '' or image_test.thumbnail_400px == None:
            check_is_thumbnail_400px = False
        else:
            check_is_thumbnail_400px = True
        if not image_test.duration:
            check_is_duration = False
        else:
            check_is_duration = True
        self.assertEquals(False, check_is_thumbnail_400px)
        self.assertEquals(False, check_is_duration)

    def test_added_obj_manually_to_db(self):
        response1 = self.client.get(self.uploaded_image_list_url)
        self.assertEquals([], response1.data)
        new_uploaded_image = UploadedImage(user=self.user1)
        new_uploaded_image.image = SimpleUploadedFile(
            name='image_test_1.png',
            content=open(f'{FAKE_FILES_TEST_PATH}image_test_1.png', 'rb').read(),
            content_type='image/png'
        )
        new_uploaded_image.save()
        if new_uploaded_image.thumbnail_400px == '' or new_uploaded_image.thumbnail_400px == None:
            check_is_thumbnail_400px = False
        else:
            check_is_thumbnail_400px = True
        if not new_uploaded_image.duration:
            check_is_duration = False
        else:
            check_is_duration = True
        self.assertEquals(False, check_is_thumbnail_400px)
        self.assertEquals(False, check_is_duration)
        qs_test_all = UploadedImage.objects.all()
        self.assertIn(new_uploaded_image, qs_test_all)
        try:
            os.remove(f'{UPLOADED_MEDIA_PATH}{new_uploaded_image.image}')
            os.remove(f'{UPLOADED_MEDIA_PATH}{new_uploaded_image.thumbnail_200px}')
        except:
            print('nie moge usunac zdjecia wgranego podczas testow, mozna dac aplikacje z logami i to uchwycic')

    def test_str_input_as_image_plan_basic(self):
        before_update_image_uploaded_objects_in_db = UploadedImage.objects.count()
        valid_image = {
            "image": 'some string',
        }
        response = self.client.post(
            self.uploaded_image_list_url,
            data=valid_image,
            format="multipart",)
        self.assertEquals(before_update_image_uploaded_objects_in_db, UploadedImage.objects.count())
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def create_3_diff_images_to_db_basic_plan(self):
        list_of_images = ['image_test_1.png', 'image_test_2.png', 'image_test_3.jpg']
        for i in list_of_images:
            ext = i.split(".")[-1]
            name = i.split(".")[0]
            full_name = f'{name}.{ext}'
            new_uploaded_image = UploadedImage(user=self.user1)
            new_uploaded_image.image = SimpleUploadedFile(
                name=full_name,
                content=open(f'{FAKE_FILES_TEST_PATH}{full_name}', 'rb').read(),
                content_type=f'image/{ext}'
            )
            new_uploaded_image.save()

    def test_list_records_return_proper_fields(self):
        self.create_3_diff_images_to_db_basic_plan()
        response = self.client.get(self.uploaded_image_list_url)
        self.assertEquals(3, len(response.data))
        self.assertEquals(response.data[0].get("image").split('.')[-1], 'png')
        self.assertEquals(response.data[2].get("image").split('.')[-1], 'jpg')
        self.assertIn('thum', response.data[1].get("thumbnail_200px").split('/')[-1])
        self.assertEquals(UploadedImage.objects.count(), len(response.data))

