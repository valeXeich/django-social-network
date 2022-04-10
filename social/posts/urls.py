from django.urls import path
from django.views.decorators.http import require_POST

from .views import PostFormView, LikeUpdate, DislikeUpdate, CommentView, DeletePostView, DeleteCommentView

app_name = 'posts'

urlpatterns = [
    path('form/create', require_POST(PostFormView.as_view()), name='form-create'),
    path('comment/create', require_POST(CommentView.as_view()), name='comment-create'),
    path('like', LikeUpdate.as_view(), name='post-like'),
    path('dislike', DislikeUpdate.as_view(), name='post-dislike'),
    path('delete/post/<int:pk>', DeletePostView.as_view(), name='post-delete'),
    path('delete/comment', DeleteCommentView.as_view(), name='comment-delete')
]
