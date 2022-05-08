from django.views.generic.base import ContextMixin

from group.forms import AvatarBackgroundGroupUpdateForm
from group.models import GroupBan
from profiles.utils import get_online_users


class CustomContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.object
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        if self.request.path == f'/group/{group.slug}' or self.request.path == f'/group/followers/{group.slug}':
            group_ban_review = GroupBan.objects.get(group=group, ban_type='comment_ban')
            context['followers_muted'] = group_ban_review.follower.all()
        context['online_users'] = get_online_users()
        context['form_group'] = AvatarBackgroundGroupUpdateForm
        return context
