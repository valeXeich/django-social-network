from django.db import models
from django.core.validators import FileExtensionValidator

from group.models import Group
from profiles.models import Profile

class Post(models.Model):
    author = models.ForeignKey(Profile, verbose_name='Автор', on_delete=models.CASCADE, related_name='post')
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE, related_name='group_post')
    liked = models.ManyToManyField(Profile, verbose_name='Лайки', default=None, related_name='likes')
    disliked = models.ManyToManyField(Profile, verbose_name='Дизлайки', default=None, related_name='dislikes')
    text = models.TextField()
    image = models.ImageField(
        upload_to='post_image',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],
        blank=True
    )
    video = models.FileField(
        upload_to='post_video/',
        validators=[FileExtensionValidator(['mp4'])],
        blank=True
    )
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Post author: {self.author}'


class Comment(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=300)
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by: {self.author}'
