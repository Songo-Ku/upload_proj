import uuid
from datetime import datetime, timedelta
from backports.zoneinfo import ZoneInfo

import pytz
from django.db import models
from django.core.validators import FileExtensionValidator
from image.constants import Plans
from image.utils import code_uploaded_filename, create_thumbnail  # ,create_image
from user.models import User
from django.conf import settings
from django.utils.timezone import activate
from django.utils import timezone


POLAND_TZ = pytz.timezone("Europe/Warsaw")


class UploadedImage(models.Model):
    image = models.ImageField(
        "uploaded image",
        upload_to=code_uploaded_filename,
        validators=[FileExtensionValidator(['jpg', 'png'])]
    )
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    thumbnail_200px = models.ImageField("Thumbnail of uploaded image 200 px", blank=True)
    thumbnail_400px = models.ImageField("Thumbnail of uploaded image 400 px", blank=True, null=True)
    duration = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    def save(self, **kwargs):
        self.thumbnail_200px = create_thumbnail(self.image, height_px=200)
        if self.user.plan in [Plans.PREMIUM, Plans.ENTERPRISE]:
            self.thumbnail_400px = create_thumbnail(self.image, height_px=400)
        super(UploadedImage, self).save(**kwargs)
        if self.user.plan == Plans.ENTERPRISE and self.duration:
            expiry_date = datetime.now(POLAND_TZ) + timedelta(seconds=self.duration)
            uuid_ = uuid.uuid4()
            exp_link = ExpiredLink(
                thumbnail=self, expiry_date=expiry_date, uuid=uuid_
            )
            exp_link.save()

    def __str__(self):
        return f' uploaded file on pk number:  {self.pk}'


class ExpiredLink(models.Model):
    uuid = models.UUIDField()
    thumbnail = models.OneToOneField(
        UploadedImage,
        on_delete=models.CASCADE,
        related_name='expired_link',
    )
    expiry_date = models.DateTimeField()

    def is_expired_standard(self):
        if self.expiry_date.tzinfo == pytz.timezone("UTC"):
            self.expiry_date.astimezone(ZoneInfo(settings.TIME_ZONE))
            expired_date_ = self.expiry_date.astimezone(ZoneInfo(settings.TIME_ZONE))
        else:
            expired_date_ = self.expiry_date
        # print(expired_date_, 'to jest czas expiry date \n\n')
        if expired_date_ < datetime.now(ZoneInfo(settings.TIME_ZONE)):
            return True
        return False

    def __str__(self):
        return f'link dla image: {self.thumbnail.pk}'


