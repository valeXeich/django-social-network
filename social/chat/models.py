from django.db import models
from django.urls import reverse

from profiles.models import Profile


class Dialog(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='dialogues')
    companion = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def get_messages_sender_list(self):
        messages_list = [message_owner for message_owner in self.owner.messages.filter(dialog=self)]
        for message_companion in self.companion.messages.all():
            messages_list.append(message_companion)
        return sorted(messages_list, key=lambda message: message.created_date, reverse=False)

    def get_absolute_url(self):
        return reverse('profiles:profile-dialog-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.owner.user.username} : {self.companion.user.username}'


class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'Dialog: {self.dialog}, sender: {self.sender.user.username}'
