from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Profile, Relationship
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out

@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Relationship)
def post_save_add_friend(sender, instance, created, **kwargs):
    sender_ = instance.sender
    receiver_ = instance.receiver
    if instance.status == 'accepted':
        sender_.friends.add(receiver_.user)
        receiver_.friends.add(sender_.user)
        sender_.save()
        receiver_.save()

# @receiver(user_logged_in)
# def got_online(sender, user, request, **kwargs):
#     user.profile.is_online = True
#     user.profile.save()
#
# @receiver(user_logged_out)
# def got_offline(sender, user, request, **kwargs):
#     user.profile.is_online = False
#     user.profile.save()
