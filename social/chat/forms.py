from django import forms
from .models import Message

class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']

    def save(self, dialog, sender):
        obj = super().save(commit=False)
        obj.dialog = dialog
        obj.sender = sender
        return obj.save()