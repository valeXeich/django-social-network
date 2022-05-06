from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from profiles.views import SearchProfileView, CustomLoginView, CustomSignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/', include('profiles.urls')),
    path('post/', include('posts.urls')),
    path('group/', include('group.urls')),
    path('chat/', include('chat.urls')),
    path('accounts/', include('allauth.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', CustomSignUpView.as_view(), name='signup'),
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
