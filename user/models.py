from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    TIER_PLAN = (
        ('Basic', 'Basic'),
        ('Premium', 'Premium'),
        ('Enterprise', 'Enterprise'),
    )
    plan = models.CharField(max_length=100, choices=TIER_PLAN, default='Basic')

    def __str__(self):
        return self.username
