from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from posts.views import RedirectView
from profiles.views import SearchProfileView

urlpatterns = [
    path('', RedirectView.as_view()),
    path('admin/', admin.site.urls),
    path('profile/', include('profiles.urls')),
    path('post/', include('posts.urls')),
    path('group/', include('group.urls')),
    path('chat/', include('chat.urls')),
    path('accounts/', include('allauth.urls')),
    path('search/', SearchProfileView.as_view(), name='search'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
