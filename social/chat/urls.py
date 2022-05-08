from django.urls import path

from .views import CreateMessageView, CreateOrGetDialog, MessageJson

app_name = 'chat'

urlpatterns = [
    path('create/message/', CreateMessageView.as_view(), name='create-message'),
    path('dialog/message', CreateOrGetDialog.as_view(), name='create-dialog'),
    path('message/<int:pk>', MessageJson.as_view())
]
