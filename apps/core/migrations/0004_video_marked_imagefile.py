# Generated by Django 3.2.4 on 2024-02-21 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_video_imagefile'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='marked_imagefile',
            field=models.ImageField(null=True, upload_to='images/', verbose_name=''),
        ),
    ]