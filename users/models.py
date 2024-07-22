from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    cash = models.IntegerField(
        default=10000,
        help_text='금액'
    )

    def __str__(self):
        return self.username
