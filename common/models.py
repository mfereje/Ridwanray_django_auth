import uuid

from django.db import models

class BaseModel(models.Model):
    id=models.UUIDField(primary_key=True,editable=False, default=uuid.uuid4)
    create_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True