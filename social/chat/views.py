from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q

from profiles.models import Profile
from .forms import SendMessageForm
from .models import Dialog

class DialogListView(ListView):
    """"Dialog list"""
    model = Dialog
    template_name = 'profile/profile_messages.html'
    context_object_name = 'dialogues'

    def get_queryset(self):
        queryset = Dialog.objects.filter(
            Q(owner=self.request.user.profile) | Q(companion=self.request.user.profile)
        )
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['profile'] = self.request.user.profile
        return context


class DialogDetailView(DetailView):
    """"Dialog room"""
    model = Dialog
    template_name = 'profile/dialog_detail.html'
    context_object_name = 'dialog'

    def get_context_data(self, *args, **kwargs):
        profile = self.request.user.profile
        dialogues = Dialog.objects.filter(
            Q(owner=self.request.user.profile) | Q(companion=self.request.user.profile)
        )
        context = super().get_context_data(*args, **kwargs)
        context['profile'] = profile
        context['form_send'] = SendMessageForm
        context['dialogues'] = dialogues
        return context


class CreateOrGetDialog(View):
    """"Create or get dialog"""
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


class CreateMessageView(FormView):
    """"Send messages"""
    form_class = SendMessageForm

    def get_success_url(self, **kwargs):
        dialog_id = self.request.POST.get('dialog_id')
        return reverse_lazy('profiles:profile-dialog-detail', kwargs={'pk': dialog_id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        dialog_id = self.request.POST.get('dialog_id')
        dialog = Dialog.objects.get(id=dialog_id)
        self.object = form.save(dialog=dialog, sender=self.request.user.profile)
        return super().form_valid(form)
