from django.db import models

# Create your models here.


class Tablo(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField(default="", blank=True)
    date_add = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.title

