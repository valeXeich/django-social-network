from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Group, GroupBan


@receiver(post_save, sender=Group)
def post_save_create_group_ban(sender, instance, created, **kwargs):
    """"Creating a ban list for a group"""
    if created:
        GroupBan.objects.create(group=instance, ban_type='ban_group')
        GroupBan.objects.create(group=instance, ban_type='comment_ban')
        