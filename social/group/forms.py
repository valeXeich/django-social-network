from django import forms

from .models import Group


class AvatarBackgroundGroupUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['avatar', 'background']

        widgets = {
            'avatar': forms.FileInput(attrs={'type': 'file'}),
            'background': forms.FileInput(attrs={'type': 'file'})}


class GroupInfoUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'staff', 'about']

        widgets = {
            'about': forms.Textarea(attrs={'rows': 4, 'id': 'textarea', 'required': 'required', 'class': 'cus-label'})}


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'avatar', 'background', 'about']

        widgets = {
            'about': forms.Textarea(attrs={'rows': 4})
        }

    def save(self, admin_group):
        obj = super().save(commit=False)
        obj.admin_group = admin_group
        return obj.save()
            