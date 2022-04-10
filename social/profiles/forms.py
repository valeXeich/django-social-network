from django import forms

from .models import Profile


class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'background']

        widgets = {
            'avatar': forms.FileInput(attrs={'type': 'file'}),
            'background': forms.FileInput(attrs={'type': 'file'})
        }