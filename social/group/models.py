from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

import posts.models
from profiles.models import Profile


class Group(models.Model):
    """"Group where users can join"""
    name = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to='group_avatar/', default='group_avatar.png')
    background = models.ImageField(default='group_background.png', upload_to='group_background/')
    admin_group = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='groups')
    staff = models.ManyToManyField(Profile, blank=True, related_name='staff_groups')
    followers = models.ManyToManyField(Profile, blank=True, related_name='follower_groups')
    about = models.TextField(max_length=500, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return f'Group: {self.name}'

    def get_absolute_url(self):
        return reverse('groups:group-detail', kwargs={'slug': self.slug})

    def get_admin_and_staff(self):
        """"List with staff and admin"""
        data = [profile.user for profile in self.staff.select_related('user').all()]
        data.append(self.admin_group.user)
        return data

    def get_likes_post_group(self):
        """Top 5 users by the number of likes on group posts"""
        follower_likes = []
        for follower in self.followers.all():
            likes_count = posts.models.Post.objects.filter(group=self, liked=follower).count()
            follower_likes.append([follower, likes_count])
        return sorted(follower_likes, key=lambda item: item[1], reverse=True)

    def get_comments_post_group(self):
        """"Top 5 users by the number of comments on group posts"""
        comments = [comment.author for comment in self.group_comments.select_related('author').all()]
        comments_count = [[follower, comments.count(follower)] for follower in self.followers.all()][:5]
        return sorted(comments_count, key=lambda item: item[1], reverse=True)

    def get_followers_ban(self):
        """"Getting users who are in the group's ban"""
        group_ban = GroupBan.objects.get(group=self, ban_type='ban_group')
        return group_ban.follower.all()

    def get_posts(self):
        """"Get group posts"""
        group_posts = self.group_post.select_related('author', 'group').prefetch_related('liked', 'disliked', 'comments').all()
        return group_posts

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class GroupBan(models.Model):
    """"
    Ban group list for banning comments
    or banning from the group
    """
    BAN_TYPE = (
        ('ban_group', 'Ban Group'),
        ('comment_ban', 'Comment ban')
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='bans')
    follower = models.ManyToManyField(Profile, related_name='group_ban', blank=True)
    ban_type = models.CharField(max_length=15, choices=BAN_TYPE)

    def __str__(self):
        return f'Group bans: {self.group.name}'
