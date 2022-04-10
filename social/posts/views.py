from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, DeleteView

from group.models import Group
from profiles.models import Profile
from .forms import PostForm, CommentForm
from .models import Post, Comment


class PostFormView(FormView):
    form_class = PostForm

    def get_success_url(self, **kwargs):
        user = self.request.user
        if self.request.POST.get('group_post') == 'group_post':
            group_id = self.request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            return reverse_lazy('groups:group-detail', kwargs={'slug': group.slug})
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
        return super().form_valid(form)


class CommentView(FormView):
    form_class = CommentForm

    def get_success_url(self):
        user = self.request.user
        if self.request.POST.get('group_slug'):
            group_slug = self.request.POST.get('group_slug')
            return reverse_lazy('groups:group-detail', kwargs={'slug': group_slug})
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
        self.object.save()
        return super().form_valid(form)

class LikeUpdate(View):

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
        return redirect('profiles:profile-detail', slug=profile.slug)

class DislikeUpdate(View):

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
        return redirect('profiles:profile-detail', slug=profile.slug)

class DeletePostView(DeleteView):
    model = Post

    def get_success_url(self, **kwargs):
        user = self.request.user
        if self.request.POST.get('group_id'):
            group_id = self.request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            return reverse_lazy('groups:group-detail', kwargs={'slug': group.slug})
        return reverse_lazy('profiles:profile-detail', kwargs={'slug': user.profile.slug})


class DeleteCommentView(View):

    def post(self, request, **kwargs):
        comment_id = request.POST.get('comment_id')
        profile_slug = request.user.profile.slug
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        if request.POST.get('group_id'):
            group_id = request.POST.get('group_id')
            group = Group.objects.get(id=group_id)
            return redirect('groups:group-detail', slug=group.slug)
        return redirect('profiles:profile-detail', slug=profile_slug)


