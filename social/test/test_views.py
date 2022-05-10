from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from chat.models import Dialog, Message
from profiles.models import Profile


class TestChatViews(TestCase):

    def setUp(self):
        self.user_james = User.objects.create_user(
            username='james',
            password='12345z'
        )
        self.user_vasya = User.objects.create(
            username='vasya',
            password='12345z'
        )
        self.profile_james = Profile.objects.get(
            user=self.user_james
        )
        self.profile_vasya = Profile.objects.get(
            user=self.user_vasya,
        )
        self.client = Client()
        self.dialog = Dialog.objects.create(
            owner=self.profile_james,
            companion=self.profile_vasya
        )
        self.message = Message.objects.create(
            dialog=self.dialog,
            sender=self.profile_james,
            text='Hello',
        )

    def test_dialog_list_view(self):
        self.client.login(username='james', password='12345z')
        response = self.client.get(reverse('profiles:profile-dialog'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile_messages.html')
        self.assertEquals(Dialog.objects.count(), 1)

    def test_dialog_detail_view(self):
        self.client.login(username='james', password='12345z')
        response = self.client.get(reverse('profiles:profile-dialog-detail', kwargs={'pk': self.dialog.id}))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/dialog_detail.html')

    def test_message_json(self):
        message = Message.objects.create(
            dialog=self.dialog,
            sender=self.profile_james,
            text='Hello',
        )
        self.client.login(username='james', password='12345z')
        response = self.client.get(reverse('chat:json_messages', kwargs={'pk': self.dialog.id}))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.headers['Content-Type'], 'application/json')

    def test_get_dialog(self):
        self.client.login(username='james', password='12345z')
        response = self.client.post(reverse('chat:create-dialog'), {'profile_id': self.profile_james.id})
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, f'/profile/messages/9')

    def test_create_message_view(self):
        self.client.login(username='james', password='12345z')
        response = self.client.post(reverse('chat:create-message'), {'dialog_id': self.dialog.id, 'text': "What's up"})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Message.objects.count(), 2)








