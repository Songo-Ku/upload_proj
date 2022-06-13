import os
from datetime import datetime, timedelta
from unittest.mock import patch

import pytz
from django.urls import reverse
from rest_framework import status

from image.fakes import read_fake_image_to_post
from image.models import UploadedImage, ExpiredLink
from rest_framework.test import APITestCase
from user.factories import UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from pathlib import Path
from django.utils import timezone

FAKE_FILES_TEST_PATH = f'{settings.BASE_DIR}/fake_files/'
UPLOADED_MEDIA_PATH = f'{settings.BASE_DIR}/uploaded_media/'
TEMP_LINKS = f'{settings.BASE_DIR}/temp/'
POLAND_TZ = pytz.timezone("Europe/Warsaw")
UTC_TZ = pytz.timezone("UTC")


class ImageListCreateViewSetEnterprisePlanTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.uploaded_image_list_url = reverse("image:images-list")
        cls.user_enterprise = UserFactory(plan="Enterprise")
        cls.uploaded_images_all = UploadedImage.objects.all()
        cls.uploaded_images_all.delete()
        super().setUpClass()

    def setUp(self):
        self.client.force_authenticate(user=self.user_enterprise)
        self.simply_upload_test_file = SimpleUploadedFile(
            name='image_test_1.png',
            content=open(f'{FAKE_FILES_TEST_PATH}image_test_1.png', 'rb').read(),
            content_type='image/png'
        )

    def tearDown(self):
        UploadedImage.objects.all().delete()
        if Path(settings.MEDIA_ROOT).is_dir():
            for file_ in os.listdir(Path(settings.MEDIA_ROOT + '/')):
                os.remove(os.path.join(settings.MEDIA_ROOT, file_))

    def uploaded_image_post_with_image_only(self):
        valid_image = {
            "image": self.simply_upload_test_file,
        }
        response = self.client.post(
            self.uploaded_image_list_url,
            data=valid_image,
            format="multipart",
        )
        return response

    def create_3_diff_images_to_db_with_duration_enterprise_tier(self):
        list_of_images = ['image_test_1.png', 'image_test_2.png', 'image_test_3.jpg']
        for name_file in list_of_images:
            new_uploaded_image = UploadedImage(user=self.user_enterprise)
            new_uploaded_image.image = read_fake_image_to_post(image_from_fakes=name_file)
            new_uploaded_image.duration = 3000
            new_uploaded_image.save()

    def create_3_diff_images_to_db_without_duration_enterprise_tier(self):
        list_of_images = ['image_test_1.png', 'image_test_2.png', 'image_test_3.jpg']
        for name_file in list_of_images:
            new_uploaded_image = UploadedImage(user=self.user_enterprise)
            new_uploaded_image.image = read_fake_image_to_post(image_from_fakes=name_file)
            new_uploaded_image.save()

    def uploaded_image_post_with_image_duration(self):
        valid_image = {
            "image": self.simply_upload_test_file,
            "duration": 3600
        }
        response = self.client.post(
            self.uploaded_image_list_url,
            data=valid_image,
            format="multipart",
        )
        return response

    def test_multiple_variants_with_post_image_enterprise_tier(self):
        expired_link_count = ExpiredLink.objects.count()
        response = self.uploaded_image_post_with_image_only()
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        uploaded_image_obj = UploadedImage.objects.get(pk=response.data.get("pk"))
        file_name_test = str(response.data.get("image").split("/")[-1])
        self.assertEquals(True, os.path.isfile(f'{settings.BASE_DIR}/uploaded_media/{file_name_test}'))
        qs_test_all = UploadedImage.objects.all()
        self.assertIn(uploaded_image_obj, qs_test_all)
        self.assertEquals(ExpiredLink.objects.count(), expired_link_count)
        self.assertIn('thum', uploaded_image_obj.thumbnail_200px.name)

    def test_enterprise_tier_has_duration(self):
        response = self.uploaded_image_post_with_image_duration()
        self.assertEquals(response.data.get('duration', False), 3600)

    def test_enterprise_tier_has_not_duration(self):
        response = self.uploaded_image_post_with_image_only()
        self.assertIsNone(response.data.get('duration'))

    def test_enterprise_tier_has_thumbnail_400px_without_duration(self):
        response = self.uploaded_image_post_with_image_only()
        self.assertIsNotNone(response.data.get('thumbnail_400px', None))
        self.assertIn('thum', response.data.get("thumbnail_400px"))

    def test_enterprise_tier_has_thumbnail_400px_with_duration(self):
        response = self.uploaded_image_post_with_image_duration()
        self.assertIsNotNone(response.data.get('thumbnail_400px', None))
        self.assertIn('thum', response.data.get("thumbnail_400px"))

    def test_enterprise_tier_has_thumbnail_200px_without_duration(self):
        response = self.uploaded_image_post_with_image_only()
        self.assertIsNotNone(response.data.get('thumbnail_200px', None))
        self.assertIn('thum', response.data.get("thumbnail_200px"))

    def test_enterprise_tier_has_thumbnail_200px_with_duration(self):
        response = self.uploaded_image_post_with_image_duration()
        self.assertIsNotNone(response.data.get('thumbnail_200px', None))
        self.assertIn('thum', response.data.get("thumbnail_200px"))

    def test_enterprise_tier_has_duration_and_exp_link(self):
        expired_link_count = ExpiredLink.objects.count()
        response = self.uploaded_image_post_with_image_duration()
        self.assertEquals(ExpiredLink.objects.count(), expired_link_count + 1)

    def test_enterprise_tier_has_not_duration_and_not_exp_link(self):
        expired_link_count = ExpiredLink.objects.count()
        response = self.uploaded_image_post_with_image_only()
        self.assertEquals(ExpiredLink.objects.count(), expired_link_count)

    # @patch('image.models.ExpiredLink.is_expired_standard')
    # def test_enterprise_tier_exp_link_is_expired(self, mock_is_expired):
    #     mock_is_expired = self.expiry_date < datetime.now(POLAND_TZ)
    #     expired_link_count = ExpiredLink.objects.count()
    #     response = self.uploaded_image_post_with_image_duration()
    #     self.assertEquals(ExpiredLink.objects.count(), expired_link_count + 1)
    # jak to zmockowac ?

    # def test_enterprise_tier_exp_link_is_not_expired(self):
    #     expired_link_count = ExpiredLink.objects.count()
    #     response = self.uploaded_image_post_with_image_duration()
    #     uploaded_image_obj = UploadedImage.objects.get(id=response.data.get("pk"))
    #     print(uploaded_image_obj.expired_link.is_expired_standard())
    #     self.assertEquals(uploaded_image_obj.expired_link.is_expired_standard(), False)

    # @patch('image.models.ExpiredLink.is_expired_standard')
    # def test_enterprise_tier_expired_link(self, mock_is_expired):
    #     mock_is_expired.return_value = False
    #     expired_link_count = ExpiredLink.objects.count()
    #     response = self.uploaded_image_post_with_image_duration()
    #     exp_link_obj = ExpiredLink.objects.get(pk=response.data.get("pk"))
    #     # print('to jest mock is exp', exp_link_obj.is_expired_standard, '\n\n')
    #     # "http://127.0.0.1:8000/temp/f0cca685-f451-44b5-a46a-ae475b32e27e/"
    #     response = self.client.get(self.uploaded_image_list_url)
    #     # print(response.data[0].get("expire_link"))
    #     response_exp_link = self.client.get(response.data[0].get("expire_link"))
    #     # print(response_exp_link)
    #     self.assertEquals(ExpiredLink.objects.count(), expired_link_count + 1)
    #     # "<HttpResponseNotFound status_code=404, "text/html">"
    #     # "<HttpResponseRedirect status_code=302, "text/html; charset=utf-8", url="/media/c6c84500-8d94-4762-84a6-62ad00c13276.png">"

    def test_check_instance_attr(self):
        expired_link_count = ExpiredLink.objects.count()
        response = self.uploaded_image_post_with_image_duration()
        exp_link_obj = ExpiredLink.objects.get(pk=response.data.get("pk"))
        # print(datetime.now(POLAND_TZ) - timedelta(days=2), ' dt from datetime \n')

        with patch.object(exp_link_obj, 'expiry_date', datetime.now(UTC_TZ) - timedelta(days=2)):
            print('utc time with 2 days subtraction \n', datetime.now(UTC_TZ) - timedelta(days=2))
            self.assertEqual(exp_link_obj.is_expired_standard(), True)
            # self.assertEqual(exp_link_obj.expiry_date, datetime.now(POLAND_TZ) - timedelta(days=2))





# testy redirectu
#


    def test_uploaded_image_saved_manually_to_db_with_duration_enterprise_tier(self):
        expired_link_count = ExpiredLink.objects.count()

    def test_uploaded_image_saved_manually_to_db_without_duration_enterprise_tier(self):
        expired_link_count = ExpiredLink.objects.count()

    def test_list_uploaded_images_with_duration(self):
        # self.create_3_diff_images_to_db_with_duration_enterprise_tier()
        pass

    def test_list_uploaded_images_without_duration(self):
        # self.create_3_diff_images_to_db_without_duration_enterprise_tier()
        pass





#     def test_added_obj_manually_to_db_enterprise(self):
#         response1 = self.client.get(self.uploaded_image_list_url)
#         self.assertEquals([], response1.data)
#         new_uploaded_image = UploadedImage(user=self.user_enterprise)
#         new_uploaded_image.image = SimpleUploadedFile(
#             name='image_test_1.png',
#             content=open(f'{FAKE_FILES_TEST_PATH}image_test_1.png', 'rb').read(),
#             content_type='image/png'
#         )
#         new_uploaded_image.save()
#         if new_uploaded_image.thumbnail_400px == '' or new_uploaded_image.thumbnail_400px == None:
#             check_is_thumbnail_400px = False
#         else:
#             check_is_thumbnail_400px = True
#         if not new_uploaded_image.duration:
#             check_is_duration = False
#         else:
#             check_is_duration = True
#         self.assertEquals(True, check_is_thumbnail_400px)
#         self.assertEquals(False, check_is_duration)
#         qs_test_all = UploadedImage.objects.all()
#         self.assertIn(new_uploaded_image, qs_test_all)
#         try:
#             os.remove(f'{UPLOADED_MEDIA_PATH}{new_uploaded_image.image}')
#             os.remove(f'{UPLOADED_MEDIA_PATH}{new_uploaded_image.thumbnail_200px}')
#             os.remove(f'{UPLOADED_MEDIA_PATH}{new_uploaded_image.thumbnail_400px}')
#
#         except:
#             print('nie moge usunac zdjecia wgranego podczas testow, mozna dac aplikacje z logami i to uchwycic')
#
#     def test_str_input_as_image_plan_enterprise(self):
#         before_update_image_uploaded_objects_in_db = UploadedImage.objects.count()
#         invalid_image = {
#             "image": 'some string',
#         }
#         response = self.client.post(
#             self.uploaded_image_list_url,
#             data=invalid_image,
#             format="multipart", )
#         self.assertEquals(before_update_image_uploaded_objects_in_db, UploadedImage.objects.count())
#         self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#     def create_3_diff_images_to_db_enterprise_plan(self):
#         list_of_images = ['image_test_1.png', 'image_test_2.png', 'image_test_3.jpg']
#         for i in list_of_images:
#             ext = i.split(".")[-1]
#             name = i.split(".")[0]
#             full_name = f'{name}.{ext}'
#             new_uploaded_image = UploadedImage(user=self.user_enterprise)
#             new_uploaded_image.image = SimpleUploadedFile(
#                 name=full_name,
#                 content=open(f'{FAKE_FILES_TEST_PATH}{full_name}', 'rb').read(),
#                 content_type=f'image/{ext}'
#             )
#             new_uploaded_image.duration = 3600
#             new_uploaded_image.save()
#
#     def test_list_records_return_proper_fields_enterprise(self):
#         time_to_left_in_minutes = 3600
#         self.create_3_diff_images_to_db_enterprise_plan()
#         response = self.client.get(self.uploaded_image_list_url)
#         self.assertEquals(3, len(response.data))
#         self.assertEquals(response.data[0].get("image").split('.')[-1], 'png')
#         self.assertEquals(response.data[2].get("image").split('.')[-1], 'jpg')
#         self.assertIn('thum', response.data[0].get("thumbnail_200px").split('/')[-1])
#         self.assertIn('thum', response.data[1].get("thumbnail_200px").split('/')[-1])
#         self.assertIn('thum', response.data[2].get("thumbnail_400px").split('/')[-1])
#         self.assertIn('thum', response.data[0].get("thumbnail_400px").split('/')[-1])
#         self.assertIn('expire_link', response.data[0].get("expire_link").split('/')[-2])
#         self.assertEquals(UploadedImage.objects.count(), len(response.data))
#
#     def test_post_expire_link_plan_enterprise(self):
#         amount_exp_link_before_post = ExpiredLink.objects.count()
#         valid_image = {
#             "image": SimpleUploadedFile(
#                 name='image_test_2.png',
#                 content=open(f'{FAKE_FILES_TEST_PATH}image_test_2.png', 'rb').read(),
#                 content_type='image/png'
#             ),
#             "duration": 3600,
#         }
#         response = self.client.post(
#             self.uploaded_image_list_url,
#             data=valid_image,
#             format="multipart",
#         )
#         self.assertEquals(response.status_code, status.HTTP_201_CREATED)
#         self.assertEquals(ExpiredLink.objects.count(), amount_exp_link_before_post+1)
#         created_image = UploadedImage.objects.get(pk=response.data.get("pk"))
#         file_name_test = str(response.data.get("image").split("/")[-1])
#         self.assertEquals(True, os.path.isfile(f'{settings.BASE_DIR}/temp/{created_image.show_exp_link()}'))
#         check_is_duration_in_request = response.data.get("duration")
#         self.assertEquals(3600, check_is_duration_in_request)
#         try:
#             os.remove(f'{settings.BASE_DIR}/uploaded_media/{file_name_test}')
#             os.remove(f'{UPLOADED_MEDIA_PATH}{created_image.thumbnail_200px}')
#             os.remove(f'{TEMP_LINKS}{created_image.show_exp_link()}')
#         except:
#             print('nie moge usunac zdjecia wgranego podczas testow, mozna dac aplikacje z logami i to uchwycic')
