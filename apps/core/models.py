from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=200)
    width = models.IntegerField(default=320)
    height = models.IntegerField(default=240)
    videofile = models.FileField(upload_to='videos/', null=True, verbose_name="")
    imagefile = models.ImageField(upload_to='images/', null=True, verbose_name="")
    marked_imagefile = models.ImageField(upload_to='images/', null=True, verbose_name="")



