from django.views.generic.base import ContextMixin

from .utils import get_online_users


class CustomContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['online_users'] = get_online_users()
        return context
