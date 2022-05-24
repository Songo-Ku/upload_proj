from django.contrib import admin
from django import forms
from datetime import datetime, timedelta
# Register your models here.
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from image.models import UploadedImage, TempUrl

admin.site.register(UploadedImage)
# admin.site.register(TempUrl)


class TempUrlAdminForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = "__all__"

    def clean_duration(self):
        # self.cleaned_data["duration"] = datetime.now() + timedelta(seconds=self.cleaned_data["duration"])
        print(self.data)
        self.cleaned_data["duration"] = int(self.data.get("duration"))
        return self.cleaned_data["duration"]

    def clean_expired(self):
        self.cleaned_data["expired"] = datetime.now() + timedelta(seconds=int(self.cleaned_data["duration"]))
        print(self.cleaned_data["expired"])
        return self.cleaned_data["expired"]


@admin.register(TempUrl)
class TempUrlAdmin(admin.ModelAdmin):
    form = TempUrlAdminForm










# @admin.register(TempUrl)
# class TempUrlAdmin(admin.ModelAdmin):
#     fields = [
#         'images',
#         'url_hash',
#         'duration'
#     ]
    # actions = [self.set_expired_date()]


class MyAdminPositiveIntigerField(ModelForm):
    def to_python(self, value):
        try:
            value = super(ModelForm, self).to_python(value)
        except self.queryset.model.DoesNotExist:
            key = self.to_field_name or 'pk'
            value = TempUrl.objects.filter(**{key: value})
            if not value.exists():
                raise ValidationError(self.error_messages['duration'], code='duration')
            else:
                value = value.first()
        return value