from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView

from posts.forms import PostForm, CommentForm
from .models import Group


class GroupDetailView(DetailView):
    model = Group
    template_name = 'group/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        context['form_post'] = PostForm
        context['form_comment'] = CommentForm
        return context


class GroupFollowView(View):

    def post(self, request, *args, **kwargs):
        group_id = request.POST.get('group_id')
        group = Group.objects.get(id=group_id)
        profile = request.user.profile
        if request.POST.get('follow'):
            group.followers.add(profile)
            group.save()
        elif request.POST.get('unfollow'):
            group.followers.remove(profile)
            group.save()
        return redirect('groups:group-detail', slug=group.slug)
