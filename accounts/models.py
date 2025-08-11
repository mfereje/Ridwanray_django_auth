from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=255)
    USERNAME_FIELD=email
    REQUIRED_FIELD:[]
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)


