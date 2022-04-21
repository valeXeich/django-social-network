from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from group.models import Group
from posts.forms import PostForm, CommentForm

from .forms import AvatarBackgroundUpdateForm, ProfileInfoUpdateForm
from .models import Profile, Relationship
from .utils import permission_create_post, check_relationship, check_friend_request, get_online_users


class ProfileDetailView(DetailView):
    """"Main Profile page"""
    model = Profile
    queryset = Profile.objects.select_related('user').prefetch_related('post').all()
    template_name = 'profile/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        receiver = check_relationship(user=self.request.user, profile=kwargs['object'])
        friend_request = check_friend_request(user=self.request.user, profile=kwargs['object'])
        context = super().get_context_data(**kwargs)
        context['form_post'] = PostForm
        context['form_comment'] = CommentForm
        context['form_ab'] = AvatarBackgroundUpdateForm
        context['check_current_user'] = permission_create_post(self.request.user)
        context['receiver'] = receiver
        context['friend_request'] = friend_request
        context['online_users'] = get_online_users()
        return context


class ProfileFriendsDetailView(DetailView):
    """"Profile friends page"""
    model = Profile
    template_name = 'profile/profile_friends.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_ab'] = AvatarBackgroundUpdateForm
        context['online_users'] = get_online_users()
        return context


class ProfileGroupsDetailView(DetailView):
    model = Profile
    template_name = 'profile/profile_groups.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_ab'] = AvatarBackgroundUpdateForm
        context['online_users'] = get_online_users()
        return context


class RelationshipCreateView(View):
    """"Cancel and send friend request"""

    def post(self, request, *args, **kwargs):
        receiver_id = request.POST.get('receiver_id')
        sender = request.user.profile
        receiver = Profile.objects.get(id=receiver_id)
        rel, created = Relationship.objects.get_or_create(sender=sender, receiver=receiver, status='send')
        if not created:
            rel.delete()
        return redirect('profiles:profile-detail', slug=receiver.slug)


class DeleteFriendView(View):

    def post(self, request, *args, **kwargs):
        current_user = request.user.profile
        friend_id = request.POST.get('profile')
        friend_delete = Profile.objects.get(id=friend_id)
        current_user.friends.remove(friend_delete.user)
        friend_delete.friends.remove(current_user.user)
        current_user.save()
        if request.POST.get('friend-page') == 'friend-page':
            return redirect('profiles:profile-friends', slug=current_user.slug)
        return redirect('profiles:profile-detail', slug=friend_delete.slug)


class AcceptFriendRequest(View):

    def post(self, request, *args, **kwargs):
        sender_id = request.POST.get('profile_sender')
        receiver = request.user.profile
        sender = Profile.objects.get(id=sender_id)
        rel = Relationship.objects.get(sender=sender, receiver=receiver, status='send')
        if request.POST.get('delete_request') == 'delete_request':
            rel.delete()
        elif request.POST.get('accept_request') == 'accept_request':
            rel.status = 'accepted'
            rel.save()
            rel.delete()
        if request.POST.get('friend-page') == 'friend-page':
            return redirect('profiles:profile-friends', slug=receiver.slug)
        return redirect('profiles:profile-detail', slug=sender.slug)


class AvatarBackgroundUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = AvatarBackgroundUpdateForm
    model = Profile

    def test_func(self):
        profile = self.get_object()
        return profile.user == self.request.user

    def get_success_url(self):
        profile_slug = self.request.POST.get('profile_slug')
        return reverse_lazy('profiles:profile-detail', kwargs={'slug': profile_slug})


class ProfileInfoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = ProfileInfoUpdateForm
    model = Profile
    template_name = 'profile/profile_about.html'
    context_object_name = 'profile'

    def test_func(self):
        profile = self.get_object()
        return profile.user == self.request.user

    def get_success_url(self):
        profile_slug = self.request.POST.get('profile_slug')
        return reverse_lazy('profiles:update-info', kwargs={'slug': profile_slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_ab'] = AvatarBackgroundUpdateForm
        context['online_users'] = get_online_users()
        return context


class SearchProfileView(ListView):
    model = Profile
    template_name = 'search.html'
    context_object_name = 'search_result'

    def get_queryset(self):
        data_input = self.request.GET.get('q')
        if len(data_input.split()) == 1:
            result = Profile.objects.filter(
                Q(first_name__icontains=data_input.strip(' ')) | Q(last_name__icontains=data_input.strip(' '))
            )
        elif len(data_input.split()) == 2:
            data_input = data_input.split()
            result = Profile.objects.filter(
                Q(first_name__icontains=data_input[0]) & Q(last_name__icontains=data_input[1]) |
                Q(last_name__icontains=data_input[0]) & Q(first_name__icontains=data_input[1])
            )
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        context['online_users'] = get_online_users()
        return context





