from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Post


@receiver(pre_delete, sender=Post)
def video_file_delete(sender, instance, **kwargs):
    """"Signal for delete video file"""
    if instance.video.name:
        instance.video.delete(False)