from django.contrib.auth.models import User
from django.db import models


class Notice(models.Model):
    type = models.CharField(max_length=100)
    user = models.ForeignKey(User, blank=False, null=False)
    log = models.TextField(null=True, blank=True)
    read = models.BooleanField(default=False)