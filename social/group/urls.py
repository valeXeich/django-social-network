from django.urls import path

from .views import GroupDetailView, GroupFollowView

app_name = 'groups'

urlpatterns = [
    path('<slug:slug>', GroupDetailView.as_view(), name='group-detail'),
    path('follow/group', GroupFollowView.as_view(), name='group-follow'),
]