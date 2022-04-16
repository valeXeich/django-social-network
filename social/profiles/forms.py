from django import forms

from .models import Profile
from django_countries.widgets import CountrySelectWidget


class AvatarBackgroundUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'background']

        widgets = {
            'avatar': forms.FileInput(attrs={'type': 'file'}),
            'background': forms.FileInput(attrs={'type': 'file'})
        }


class ProfileInfoUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'about', 'country', 'gender', 'date_birth']

        YEARS = [year for year in range(1940, 2021)]

        widgets = {
            'first_name': forms.TextInput(attrs={'id': 'input', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'required': 'required'}),
            'about': forms.Textarea(attrs={'rows': 4, 'id': 'textarea', 'required': 'required', 'class': 'cus-label'}),
            'country': CountrySelectWidget(attrs={'placeholder': 'Country'}),
            'gender': forms.RadioSelect(attrs={'checked': 'checked', 'name': 'radio',}),
            'date_birth': forms.SelectDateWidget(empty_label=('Select year', 'Select month', 'Select day'), years=YEARS),
        }