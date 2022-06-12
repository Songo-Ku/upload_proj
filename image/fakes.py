from PIL import Image
import tempfile
from django.conf import settings

from django.core.files.uploadedfile import SimpleUploadedFile
FAKE_FILES_TEST_PATH = f'{settings.BASE_DIR}/fake_files/'
UPLOADED_MEDIA_PATH = f'{settings.BASE_DIR}/uploaded_media/'
TEMP_LINKS = f'{settings.BASE_DIR}/temp/'


def read_fake_image_to_post(image_from_fakes='image_test_1.png'):
    ext = image_from_fakes.split(".")[-1]
    name = image_from_fakes.split(".")[0]
    simply_upload_test_file = SimpleUploadedFile(
        name=image_from_fakes,
        content=open(f'{FAKE_FILES_TEST_PATH}{image_from_fakes}', 'rb').read(),
        content_type=f'image/{ext}'
    )
    return simply_upload_test_file


def create_fake_image_jpg_to_post():
    image = Image.new('RGB', (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file)
    tmp_file.seek(0)
    return tmp_file