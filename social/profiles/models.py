from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django_countries.fields import CountryField


class Profile(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(max_length=500, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    country = CountryField(blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)
    avatar = models.ImageField(default='avatars/avatar.png', upload_to='avatars/')
    background = models.ImageField(default='background/background.png', upload_to='background/')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    is_online = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profiles:profile-detail', kwargs={'slug': self.slug})

    def get_friends_list(self):
        return self.user.friends.all()

    def get_friends_request(self):
        sender_list = []
        for receiver in self.receiver.all():
            sender_list.append(receiver.sender)
        return sender_list

    def get_post_list(self):
        post_list = []
        for post in self.post.all():
            if post.group == None:
                post_list.append(post)
        return post_list

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        return super().save(*args, **kwargs)


class Relationship(models.Model):
    STATUS_CHOICES = (
        ('send', 'send'),
        ('accepted', 'accepted')
    )

    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} : {self.receiver} - {self.status}'


