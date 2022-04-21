from django.urls import path

from .views import (
    GroupDetailView,
    GroupFollowView,
    AvatarBackgroundGroupUpdateView,
    GroupInfoUpdateView,
    GroupFollowersView,
    GroupBanView,
    GroupUnBan,
    GroupBanList,
    GroupAboutView,
    SearchGroupView,
)

app_name = 'groups'

urlpatterns = [
    path('<slug:slug>', GroupDetailView.as_view(), name='group-detail'),
    path('follow/group', GroupFollowView.as_view(), name='group-follow'),
    path('update/avatar/<slug:slug>', AvatarBackgroundGroupUpdateView.as_view(), name='group-avatar'),
    path('update/info/<slug:slug>', GroupInfoUpdateView.as_view(), name='group-update'),
    path('followers/<slug:slug>', GroupFollowersView.as_view(), name='group-followers'),
    path('about/<slug:slug>', GroupAboutView.as_view(), name='group-about'),
    path('ban/list/<slug:slug>', GroupBanList.as_view(), name='group-ban-list'),
    path('ban/', GroupBanView.as_view(), name='group-ban'),
    path('unban/', GroupUnBan.as_view(), name='group-unban'),
    path('search/', SearchGroupView.as_view(), name='search-group'),
]