from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from profiles.models import Profile


class Group(models.Model):
    name = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to='group_avatar/', default='group_avatar.png')
    background = models.ImageField(default='group_background.png', upload_to='group_background/')
    admin_group = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='groups')
    staff = models.ManyToManyField(Profile, blank=True, related_name='staff_groups')
    followers = models.ManyToManyField(Profile, blank=True, related_name='follower_groups')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return f'Group: {self.name}'

    def get_absolute_url(self):
        return reverse('groups:group-detail', kwargs={'slug': self.slug})

    def get_admin_and_staff(self):
        data = [profile.user for profile in self.staff.all()]
        data.append(self.admin_group.user)
        return data

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
