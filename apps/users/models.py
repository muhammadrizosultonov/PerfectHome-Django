from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # you can extend later
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.username