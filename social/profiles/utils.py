from posts.models import Comment, Post
from .models import Profile, Relationship


def permission_create_post(user):
    if user.is_authenticated:
        profile = Profile.objects.get(user=user)
        if user.profile.slug == profile.slug:
            return True
    else:
        return False

def check_relationship(user, profile):
    if user != profile.user and user not in profile.friends.all():
        try:
            receiver = Relationship.objects.get(sender=user.profile, receiver=profile, status='send').receiver
            return 'receiver'
        except Relationship.DoesNotExist:
            return 'not receiver'

def check_friend_request(user, profile):
    flag = False
    for rel in profile.sender.all():
        if user.profile == rel.receiver and rel.status == 'send':
            flag = True
    return flag

