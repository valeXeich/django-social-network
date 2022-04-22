import online_users.models
from datetime import timedelta

from .models import Relationship


def check_relationship(user, profile):
    """"Checking the recipient of a friendship request"""
    if not user.is_anonymous:
        if user != profile.user and user not in profile.friends.all():
            try:
                Relationship.objects.get(sender=user.profile, receiver=profile, status='send').receiver
                return 'receiver'
            except Relationship.DoesNotExist:
                return 'not receiver'

def check_friend_request(user, profile):
    """"Checking the sender of a friendship request"""
    flag = False
    for rel in profile.sender.all():
        if user.profile == rel.receiver and rel.status == 'send':
            flag = True
    return flag


def get_online_users():
    """"Online users"""
    user_online = online_users.models.OnlineUserActivity.get_user_activities(timedelta(seconds=60))
    users = [online.user.profile for online in user_online]
    return users

