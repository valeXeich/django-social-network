from django import forms
from django_countries.widgets import CountrySelectWidget

from allauth.account.forms import SignupForm, LoginForm

from .models import Profile


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


class NewSignupForm(SignupForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        first_name_widget = forms.TextInput(attrs={'id': 'signup_input_first_name'})
        last_name_widget = forms.TextInput(attrs={'id': 'signup_input_last_name'})
        email_widget = forms.TextInput(attrs={'id': 'signup_input_email'})
        username_widget = forms.TextInput(attrs={'id': 'signup_input_username'})
        password_widget = forms.PasswordInput(attrs={'class': 'signup_input_password'})
        self.fields['first_name'] = forms.CharField(label='First name', widget=first_name_widget)
        self.fields['last_name'] = forms.CharField(label='Last name', widget=last_name_widget)
        self.fields['username'] = forms.CharField(label='Username', widget=username_widget)
        self.fields['email'] = forms.EmailField(label='E-mail', widget=email_widget)
        self.fields['password1'] = forms.CharField(label='Password', widget=password_widget)
        self.fields['password2'] = forms.CharField(label='Password (again)', widget=password_widget)


class NewLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        email_widget = forms.TextInput(attrs={'id': 'login_input_email'})
        password_widget = forms.PasswordInput(attrs={'id': 'login_input_password'})
        self.fields['login'] = forms.EmailField(label='E-mail', widget=email_widget)
        self.fields['password'] = forms.CharField(label='Password', widget=password_widget)
