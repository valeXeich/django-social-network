from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView, ListView, FormView, DeleteView

from posts.forms import PostForm, CommentForm
from profiles.forms import AvatarBackgroundUpdateForm
from profiles.models import Profile

from .mixins import CustomContextMixin
from .models import Group, GroupBan
from .forms import AvatarBackgroundGroupUpdateForm, GroupInfoUpdateForm, GroupCreateForm


class GroupDetailView(CustomContextMixin, DetailView):
    """"Group main page"""
    model = Group
    template_name = 'group/group_detail.html'
    queryset = Group.objects.select_related('admin_group').prefetch_related('followers').all()
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_post'] = PostForm
        context['form_comment'] = CommentForm
        return context


class AvatarBackgroundGroupUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Updating the avatar and background"""
    form_class = AvatarBackgroundGroupUpdateForm
    model = Group

    def test_func(self):
        """"Access only for admins"""
        group = self.get_object()
        profile = self.request.user.profile
        return group.admin_group == profile

    def get_success_url(self, **kwargs):
        group_slug = self.request.POST.get('group_slug')
        return reverse_lazy('groups:group-detail', kwargs={'slug': group_slug})


class GroupInfoUpdateView(LoginRequiredMixin, UserPassesTestMixin, CustomContextMixin, UpdateView):
    """"Updating group information"""
    form_class = GroupInfoUpdateForm
    model = Group
    template_name = 'group/group_update.html'

    def test_func(self):
        """"Access only for admins"""
        group = self.get_object()
        profile = self.request.user.profile
        return profile == group.admin_group

    def get_success_url(self, **kwargs):
        group_slug = self.request.POST.get('group_slug')
        return reverse_lazy('groups:group-update', kwargs={'slug': group_slug})


class GroupFollowersView(CustomContextMixin, DetailView):
    """"List group's followers"""
    model = Group
    template_name = 'group/group_followers.html'

    def get_context_data(self, **kwargs):
        group = self.get_object()
        context = super().get_context_data(**kwargs)
        context['followers'] = group.followers.all()
        return context


class GroupBanList(LoginRequiredMixin, UserPassesTestMixin, CustomContextMixin, DetailView):
    """"List of banned users"""
    model = Group
    template_name = 'group/group_ban_list.html'

    def test_func(self):
        """"Admin and staff access"""
        group = self.get_object()
        user = self.request.user
        return user in group.get_admin_and_staff()


class GroupAboutView(CustomContextMixin, DetailView):
    """"Group Information"""
    model = Group
    template_name = 'group/group_about.html'


class GroupFollowView(LoginRequiredMixin, View):
    """"Follow group"""

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


class GroupBanView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Ban a user"""

    def test_func(self):
        """"Admin and staff access"""
        group_id = self.request.POST.get('group_id')
        group = Group.objects.get(id=group_id)
        profile = self.request.user.profile
        return profile in group.get_admin_and_staff()

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


class GroupUnBan(LoginRequiredMixin, UserPassesTestMixin, View):
    """"Unban a user"""

    def test_func(self):
        """"Admin and staff access"""
        group_id = self.request.POST.get('group_id')
        group = Group.objects.get(id=group_id)
        profile = self.request.user.profile
        return profile in group.get_admin_and_staff()

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


class CreateGroup(LoginRequiredMixin, CustomContextMixin, FormView):
    """Creating group"""
    form_class = GroupCreateForm
    template_name = 'group/create_group.html'

    def get_success_url(self):
        return reverse_lazy('groups:create-group')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(admin_group=self.request.user.profile)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_ab'] = AvatarBackgroundUpdateForm
        return context


class SearchGroupView(CustomContextMixin, ListView):
    """"Group search"""
    model = Group
    template_name = 'search_group.html'
    context_object_name = 'search_result'

    def get_queryset(self):
        data_input = self.request.GET.get('search_group')
        queryset = Group.objects.filter(name__icontains=data_input)
        return queryset


class DeleteGroup(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Deleting a group"""
    model = Group

    def test_func(self):
        """"Access only for admins"""
        group = self.get_object()
        profile = self.request.user.profile
        return profile == group.admin_group

    def get_success_url(self, **kwargs):
        profile_slug = self.request.user.profile.slug
        return reverse_lazy('profiles:profile-detail', kwargs={'slug': profile_slug})

