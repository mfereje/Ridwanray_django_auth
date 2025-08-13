from datetime import datetime, timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from common.models import BaseModel
from .manager import CustomUserManager

class User(BaseModel,AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=255)
    USERNAME_FIELD="email"
    REQUIRED_FIELD:[]
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)



    objects=CustomUserManager()


class PendingUser(BaseModel):
    email=models.EmailField()
    password=models.CharField(max_length=255)
    verification_code=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)



    def is_valild(self)->bool:
        life_span_in_seconds=20*60
        now=datetime.now(timezone.utc)
        timediff=now-self.created_at
        timediff=timediff.total_seconds()

        if timediff > life_span_in_seconds:
            return False
        
        return True



