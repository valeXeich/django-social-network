from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, DeleteView, ListView

from group.models import Group, GroupBan
from profiles.models import Profile
from profiles.utils import get_online_users

from .forms import PostForm, CommentForm
from .models import Post, Comment
from .utils import get_posts_for_user
from .tasks import upload_to_vimeo, delete_video_from_vimeo


class PostFormView(LoginRequiredMixin, FormView):
    """"Creating post"""
    form_class = PostForm

    def get_success_url(self, **kwargs):
        user = self.request.user
        if self.request.POST.get('group_post'):
            group_id = self.request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            return reverse_lazy('groups:group-detail', kwargs={'slug': group.slug})
        elif self.request.POST.get('feed'):
            return reverse_lazy('posts:news')
        return reverse_lazy('profiles:profile-detail', kwargs={'slug': user.profile.slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user = self.request.user
        self.object = form.save(commit=False)
        self.object.author = user.profile
        if self.request.POST.get('group_post') == 'group_post':
            group_id = self.request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            self.object.group = group
        self.object.save()
        if form.cleaned_data['video']:
            post = Post.objects.get(id=self.object.id)
            upload_to_vimeo.delay(f'media/{post.video}', user.profile.slug, post.text, post.id)
            messages.success(self.request, 'Your video is uploading, please wait a few minutes.')
        return super().form_valid(form)


class CommentView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """"Creating commentary"""
    form_class = CommentForm

    def test_func(self):
        """"Ban on writing comments, for those on the ban list"""
        profile = self.request.user.profile
        if self.request.POST.get('group_slug'):
            group_slug = self.request.POST.get('group_slug')
            group = Group.objects.get(slug=group_slug)
            group_ban_review = GroupBan.objects.get(group=group, ban_type='comment_ban')
            return profile not in group_ban_review.follower.all()
        return True

    def get_success_url(self):
        user = self.request.user
        if self.request.POST.get('group_slug'):
            group_slug = self.request.POST.get('group_slug')
            return reverse_lazy('groups:group-detail', kwargs={'slug': group_slug})
        elif self.request.POST.get('feed'):
            return reverse_lazy('posts:news')
        return reverse_lazy('profiles:profile-detail', kwargs={'slug': user.profile.slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user = self.request.user
        post_id = self.request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        self.object = form.save(commit=False)
        self.object.author = user.profile
        self.object.post = post
        if self.request.POST.get('group_slug'):
            group_slug = self.request.POST.get('group_slug')
            group = Group.objects.get(slug=group_slug)
            self.object.group = group
        self.object.save()
        return super().form_valid(form)


class LikeUpdate(LoginRequiredMixin, View):
    """"Like and remove"""

    def post(self, request, **kwargs):
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=request.user)
        if profile in post.liked.all():
            post.liked.remove(profile)
        else:
            post.liked.add(profile)
        post.save()
        if request.POST.get('group_id'):
            group_id = request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            return redirect('groups:group-detail', slug=group.slug)
        elif request.POST.get('feed'):
            return redirect('posts:news')
        return redirect('profiles:profile-detail', slug=profile.slug)


class DislikeUpdate(LoginRequiredMixin, View):
    """"Dislike and remove"""

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=request.user)
        if profile in post.disliked.all():
            post.disliked.remove(profile)
        else:
            post.disliked.add(profile)
        post.save()
        if request.POST.get('group_id'):
            group_id = request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            return redirect('groups:group-detail', slug=group.slug)
        elif request.POST.get('feed'):
            return redirect('posts:news')
        return redirect('profiles:profile-detail', slug=profile.slug)


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """"Delete post"""
    model = Post

    def post(self, request, *args, **kwargs):
        if self.get_object().vimeo_url:
            vimeo_url = self.get_object().vimeo_url
            vimeo_id = vimeo_url.split('/')[-1]
            delete_video_from_vimeo.delay(vimeo_id)
        return super().post(request, *args, **kwargs)

    def test_func(self):
        """"
        Only those in admin and staff can delete group post
        """
        post = self.get_object()
        profile = self.request.user.profile
        if self.request.POST.get('group_id'):
            group_id = self.request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            if profile.user in group.get_admin_and_staff():
                return True
            else:
                return False
        return profile == post.author

    def get_success_url(self, **kwargs):
        user = self.request.user
        if self.request.POST.get('group_id'):
            group_id = self.request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            return reverse_lazy('groups:group-detail', kwargs={'slug': group.slug})
        elif self.request.POST.get('feed'):
            return reverse_lazy('posts:news')
        return reverse_lazy('profiles:profile-detail', kwargs={'slug': user.profile.slug})


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """"Delete comment"""

    def test_func(self):
        """"
        Admin and staff can delete comments on a group post
        """
        comment_id = self.request.POST.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        profile = self.request.user.profile
        if self.request.POST.get('group_id'):
            group_id = self.request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            if profile.user in group.get_admin_and_staff():
                return True
            else:
                return False
        return profile == comment.author

    def post(self, request, **kwargs):
        comment_id = request.POST.get('comment_id')
        profile_slug = request.user.profile.slug
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        if request.POST.get('group_id'):
            group_id = request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            return redirect('groups:group-detail', slug=group.slug)
        elif self.request.POST.get('feed'):
            return redirect('posts:news')
        return redirect('profiles:profile-detail', slug=profile_slug)


class NewsView(LoginRequiredMixin, ListView):
    """"News feed"""
    model = Post
    template_name = 'post/news_list.html'

    def get_context_data(self, *args, **kwargs):
        posts = get_posts_for_user(self.request.user.profile)
        context = super().get_context_data(*args, **kwargs)
        context['form_post'] = PostForm
        context['form_comment'] = CommentForm
        context['profile'] = self.request.user.profile
        context['posts'] = posts
        context['online_users'] = get_online_users()
        return context


class RedirectView(LoginRequiredMixin, View):
    """"View to redirect from '/' to 'post/feed'"""
    def get(self, request, *args, **kwargs):
        return redirect('posts:news')
