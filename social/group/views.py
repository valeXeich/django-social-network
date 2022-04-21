from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView, ListView

from posts.forms import PostForm, CommentForm
from profiles.models import Profile
from profiles.utils import get_online_users
from .models import Group, GroupBan
from .forms import AvatarBackgroundGroupUpdateForm, GroupInfoUpdateForm


class GroupDetailView(DetailView):
    model = Group
    template_name = 'group/group_detail.html'
    queryset = Group.objects.select_related('admin_group').prefetch_related('followers').all()
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        group = self.get_object()
        group_ban_review = GroupBan.objects.get(group=group, ban_type='comment_ban')
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        context['form_post'] = PostForm
        context['form_comment'] = CommentForm
        context['form_group'] = AvatarBackgroundGroupUpdateForm
        context['followers_muted'] = group_ban_review.follower.select_related('author_comments').all()
        context['online_users'] = get_online_users()
        return context


class AvatarBackgroundGroupUpdateView(UpdateView):
    form_class = AvatarBackgroundGroupUpdateForm
    model = Group

    def get_success_url(self, **kwargs):
        group_slug = self.request.POST.get('group_slug')
        return reverse_lazy('groups:group-detail', kwargs={'slug': group_slug})


class GroupInfoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = GroupInfoUpdateForm
    model = Group
    template_name = 'group/group_update.html'

    def test_func(self):
        group_admin = self.get_object().admin_group
        return self.request.user.profile == group_admin

    def get_success_url(self, **kwargs):
        group_slug = self.request.POST.get('group_slug')
        return reverse_lazy('groups:group-update', kwargs={'slug': group_slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        context['form_group'] = AvatarBackgroundGroupUpdateForm
        context['online_users'] = get_online_users()
        return context


class GroupFollowersView(DetailView):
    model = Group
    template_name = 'group/group_followers.html'

    def get_context_data(self, **kwargs):
        group = self.get_object()
        group_ban_review = GroupBan.objects.get(group=group, ban_type='comment_ban')
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        context['followers_muted'] = group_ban_review.follower.all()
        context['online_users'] = get_online_users()
        return context


class GroupBanList(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Group
    template_name = 'group/group_ban_list.html'

    def test_func(self):
        group = self.get_object()
        profile = self.request.user.profile
        return profile in group.staff.all() or profile == group.admin_group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        context['online_users'] = get_online_users()
        return context


class GroupAboutView(DetailView):
    model = Group
    template_name = 'group/group_about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        context['online_users'] = get_online_users()
        return context


class GroupFollowView(View):

    def post(self, request, *args, **kwargs):
        group_id = request.POST.get('group_id')
        group = Group.objects.get(id=group_id)
        profile = request.user.profile
        group_ban = GroupBan.objects.get(group=group, ban_type='ban_group')
        if profile in group_ban.follower.all():
            return HttpResponse(status=403)
        if request.POST.get('follow'):
            group.followers.add(profile)
            group.save()
        elif request.POST.get('unfollow'):
            group.followers.remove(profile)
            group.save()
        if request.POST.get('from_profile'):
            profile_slug = request.POST.get('from_profile')
            return redirect('profiles:profile-groups', slug=profile_slug)
        return redirect('groups:group-detail', slug=group.slug)


class GroupBanView(View):

    def post(self, request, *args, **kwargs):
        group_id = request.POST.get('group_id')
        profile_id = request.POST.get('profile_id')
        group = Group.objects.get(id=group_id)
        profile = Profile.objects.get(id=profile_id)
        if request.POST.get('mute_profile'):
            group_ban_mute = GroupBan.objects.get(group=group, ban_type='comment_ban')
            group_ban_mute.follower.add(profile)
        elif request.POST.get('ban_profile'):
            group_ban = GroupBan.objects.get(group=group, ban_type='ban_group')
            group_ban.follower.add(profile)
            group.followers.remove(profile)
        return redirect('groups:group-followers', slug=group.slug)


class GroupUnBan(View):

    def post(self, request, *args, **kwargs):
        group_id = request.POST.get('group_id')
        profile_id = request.POST.get('profile_id')
        group = Group.objects.get(id=group_id)
        profile = Profile.objects.get(id=profile_id)
        if request.POST.get('unmute_profile'):
            group_ban_mute = GroupBan.objects.get(group=group, ban_type='comment_ban')
            group_ban_mute.follower.remove(profile)
        elif request.POST.get('unban_profile'):
            group_ban = GroupBan.objects.get(group=group, ban_type='ban_group')
            group_ban.follower.remove(profile)
            return redirect('groups:group-ban-list', slug=group.slug)
        return redirect('groups:group-followers', slug=group.slug)


class SearchGroupView(ListView):
    model = Group
    template_name = 'search_group.html'
    context_object_name = 'search_result'

    def get_queryset(self):
        data_input = self.request.GET.get('search_group')
        queryset = Group.objects.filter(name__icontains=data_input)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['profile'] = self.request.user.profile
        context['online_users'] = get_online_users()
        return context
