from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter


class MyAccountAdapter(DefaultAccountAdapter):
    """"Redirect to profile after logging"""
    
    def get_login_redirect_url(self, request):
        return reverse('profiles:profile-detail', kwargs={'slug': request.user.profile.slug})

    def get_email_confirmation_redirect_url(self, request):
        return reverse('profiles:profile-detail', kwargs={'slug': request.user.profile.slug})
