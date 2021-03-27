from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Tablo(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField(default="", blank=True)
    date_add = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=False)
    author = models.ForeignKey(User, related_name='authors', on_delete=models.PROTECT, blank=True)

    def __str__(self):
        return self.title

