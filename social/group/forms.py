from django import forms

from .models import Group


class AvatarBackgroundGroupUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['avatar', 'background']

        widgets = {
            'avatar': forms.FileInput(attrs={'type': 'file'}),
            'background': forms.FileInput(attrs={'type': 'file'})
        }


class GroupInfoUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'staff', 'about']

        widgets = {
            'about': forms.Textarea(attrs={'rows': 4, 'id': 'textarea', 'required': 'required', 'class': 'cus-label'})
        }