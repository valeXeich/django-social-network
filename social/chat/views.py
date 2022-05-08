from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q

from profiles.models import Profile

from .forms import SendMessageForm
from .mixins import CustomContextMixin
from .models import Dialog, Message


class DialogListView(LoginRequiredMixin, CustomContextMixin, ListView):
    """"User Dialogs"""
    model = Dialog
    template_name = 'profile/profile_messages.html'
    context_object_name = 'dialogues'

    def get_queryset(self):
        queryset = Dialog.objects.filter(
            Q(owner=self.request.user.profile) | Q(companion=self.request.user.profile)
        ).select_related('owner', 'companion')
        return queryset


class DialogDetailView(LoginRequiredMixin, UserPassesTestMixin, CustomContextMixin, DetailView):
    """"Dialogue room"""
    model = Dialog
    template_name = 'profile/dialog_detail.html'
    context_object_name = 'dialog'

    def test_func(self):
        dialog = self.get_object()
        profile = self.request.user.profile
        return profile == dialog.owner or profile == dialog.companion

    def get_context_data(self, *args, **kwargs):
        dialogues = Dialog.objects.filter(
            Q(owner=self.request.user.profile) | Q(companion=self.request.user.profile)
        ).select_related('owner', 'companion')
        context = super().get_context_data(*args, **kwargs)
        context['form_send'] = SendMessageForm
        context['dialogues'] = dialogues
        return context


class MessageJson(View):
    """"Message json response for chat"""
    def get(self, request, pk, *args, **kwargs):
        dialog = Dialog.objects.get(pk=pk)
        context = {
            'messages': dialog.get_messages_sender(),
            'profile_id': request.user.profile.id,
            'dialog_companion_id': dialog.companion.id,
            'dialog_owner_id': dialog.owner.id
        }
        return JsonResponse(context)


class CreateOrGetDialog(LoginRequiredMixin, View):
    """"View to get dialog or create"""
    def post(self, request, *args, **kwargs):
        profile_id = request.POST.get('profile_id')
        profile = Profile.objects.get(id=profile_id)
        try:
            dialog = Dialog.objects.get(
                Q(owner=request.user.profile, companion=profile) | Q(owner=profile, companion=request.user.profile)
            )
        except Dialog.DoesNotExist:
            dialog = Dialog.objects.create(owner=request.user.profile, companion=profile)
        return redirect('profiles:profile-dialog-detail', pk=dialog.pk)


class CreateMessageView(LoginRequiredMixin, FormView):
    """"Sending a message to an interlocutor"""
    form_class = SendMessageForm
    template_name = 'profile/dialog_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        return context

    def get_success_url(self, **kwargs):
        dialog_id = self.request.POST.get('dialog_id')
        return reverse_lazy('profiles:profile-dialog-detail', kwargs={'pk': dialog_id})

    def post(self, request, *args, **kwargs):
        form = SendMessageForm(request.POST)
        if form.is_valid():
            dialog_id = request.POST.get('dialog_id')
            dialog = Dialog.objects.get(id=dialog_id)
            text = request.POST.get('text')
            Message.objects.create(dialog=dialog, sender=request.user.profile, text=text)
            return HttpResponse('Success')
        else:
            return self.form_invalid(form)


