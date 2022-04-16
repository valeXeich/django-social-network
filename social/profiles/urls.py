from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    ProfileDetailView,
    ProfileFriendsDetailView,
    RelationshipCreateView,
    DeleteFriendView,
    AcceptFriendRequest,
    ProfileGroupsDetailView,
    AvatarBackgroundUpdateView,
    ProfileInfoUpdateView,
    MessagesView,
)

app_name = 'profiles'

urlpatterns = [
    path('<slug:slug>', ProfileDetailView.as_view(), name='profile-detail'),
    path('<slug:slug>/friends', ProfileFriendsDetailView.as_view(), name='profile-friends'),
    path('<slug:slug>/groups', ProfileGroupsDetailView.as_view(), name='profile-groups'),
    path('<slug:slug>/messages', MessagesView.as_view(), name='profile-messages'),
    path('relationship/send-cancel', RelationshipCreateView.as_view(), name='cancel-or-send-friend-request'),
    path('delete/friend', DeleteFriendView.as_view(), name='delete-friend'),
    path('accept/friend', AcceptFriendRequest.as_view(), name='accept-friend'),
    path('update/avatar/<slug:slug>', AvatarBackgroundUpdateView.as_view(), name='update-avatar'),
    path('update/info/<slug:slug>', ProfileInfoUpdateView.as_view(), name='update-info'),
]
