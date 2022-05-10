
from django.test import TestCase
from django.contrib.auth.models import User

from chat.models import Dialog, Message
from posts.models import Post, Comment
from profiles.models import Profile, Relationship
from group.models import Group, GroupBan

class TestMixin:

    def setUp(self):
        self.user_james = User.objects.create(
            username='james',
            password='12345z'
        )
        self.user_vasya = User.objects.create(
            username='vasya',
            password='12345z'
        )
        self.profile_james = Profile.objects.get(
            user=self.user_james
        )
        self.admin = self.profile_james
        self.profile_james.first_name = 'James'
        self.profile_james.last_name = 'Bond'
        self.profile_james.save()
        self.profile_vasya = Profile.objects.get(
            user=self.user_vasya,
        )
        self.profile_vasya.first_name = 'Vasya'
        self.profile_vasya.last_name = 'Pupkin'
        self.profile_vasya.save()
        self.group = Group.objects.create(
            name='Manga fans',
            admin_group=self.admin,
        )


class TestDialogAndMessageModel(TestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.dialog = Dialog.objects.create(
            owner=self.profile_james,
            companion=self.profile_vasya
        )
        self.message = Message.objects.create(
            dialog=self.dialog,
            sender=self.profile_james,
            text='Hello',
        )

    def test_dialog_get_messages_sender(self):
        total = 0
        expected_fields = ['id', 'dialog_id', 'sender_id', 'text', 'created_date', 'avatar_url']
        result = self.dialog.get_messages_sender()
        for field in result[0].keys():
            if field in expected_fields:
                total += 1
        self.assertEquals(len(expected_fields), total)

    def test_dialog_get_absolute_url(self):
        url = self.dialog.get_absolute_url()
        self.assertEquals('/profile/messages/1', url)

    def test_dialog_str_(self):
        self.assertEquals(self.dialog.__str__(), 'james : vasya')

    def test_message_str_(self):
        self.assertEquals(self.message.__str__(), 'Dialog: james : vasya, sender: james')


class TestGroupAndGroupBanModel(TestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.user_ichigo = User.objects.create(
            username='ichigo',
            password='12345z'
        )
        self.user_follower_drake = User.objects.create(
            username='Drake',
            password='12345z'
        )
        self.user_follower_sasuke = User.objects.create(
            username='Sasuke',
            password='12345z'
        )
        self.profile_follower_drake = Profile.objects.get(
            user=self.user_follower_drake
        )
        self.profile_follower_drake.first_name = 'Drake'
        self.profile_follower_drake.last_name = 'Wolf'
        self.profile_follower_drake.save()
        self.profile_follower_sasuke = Profile.objects.get(
            user=self.user_follower_sasuke
        )
        self.profile_follower_sasuke.first_name = 'Sasuke'
        self.profile_follower_sasuke.last_name = 'Uchiha'
        self.profile_follower_sasuke.save()
        self.profile_ichigo = Profile.objects.get(
            user=self.user_ichigo
        )
        self.profile_ichigo.first_name = 'Ichigo'
        self.profile_ichigo.last_name = 'Kurosaki'
        self.profile_ichigo.save()
        self.group.staff.set([self.profile_vasya.pk, self.profile_ichigo.pk])
        self.post_group_1, self.post_group_2, self.post_group_3 = [
            Post.objects.create(
                author=self.admin,
                group=self.group,
                text=f'Best group {i}'
            ) for i in range(1, 4)
        ]

    def test_group_get_absolute_url(self):
        self.assertEquals('/group/manga-fans', self.group.get_absolute_url())

    def test_group_get_admin_and_staff(self):
        expect = [self.user_vasya, self.user_ichigo, self.admin.user]
        result = self.group.get_admin_and_staff()
        self.assertEquals(result, expect)

    def test_group_get_likes_post_group(self):

        self.post_group_1.liked.add(self.profile_follower_sasuke)
        self.post_group_2.liked.add(self.profile_follower_sasuke)
        self.post_group_3.liked.add(self.profile_follower_drake)

        self.follower_likes_expect = []
        for follower in self.group.followers.all():
            likes_count = Post.objects.filter(group=self.group, liked=follower).count()
            self.follower_likes_expect.append([follower, likes_count])
        self.follower_likes_expect = sorted(self.follower_likes_expect, key=lambda item: item[1], reverse=True)
        self.assertEquals(self.group.get_likes_post_group(), self.follower_likes_expect)

    def test_group_get_comments_post_group(self):
        authors = [self.profile_follower_sasuke, self.profile_follower_drake, self.profile_vasya]
        posts = [self.post_group_1, self.post_group_2, self.post_group_3]
        self.group.followers.set([self.profile_follower_drake.id, self.profile_follower_sasuke.id])
        self.comment_1, self.comment_2, self.comment_3 = [
            Comment.objects.create(
                author=authors[i],
                post=posts[i],
                group=self.group,
                text=f'Comment {1+i}'
            ) for i in range(3)
        ]
        comments = [comment.author for comment in self.group.group_comments.all()]
        comments_count = [[follower, comments.count(follower)] for follower in self.group.followers.all()][:5]
        expect = sorted(comments_count, key=lambda item: item[1], reverse=True)
        result = self.group.get_comments_post_group()
        self.assertEquals(result, expect)

    def test_group_get_followers_ban(self):

        group_ban = GroupBan.objects.get(group=self.group, ban_type='ban_group')
        group_ban.follower.set([self.profile_vasya.id, self.profile_ichigo.id])
        expect = group_ban.follower.all()
        result = self.group.get_followers_ban()
        self.assertEquals(list(result), list(expect))

    def test_group_get_posts(self):
        expect = self.group.group_post.all().order_by('-created_date')
        result = self.group.get_posts()
        self.assertEquals(list(result), list(expect))


class TestProfile(TestMixin, TestCase):

    def test_profile_get_absolute_url(self):
        self.assertEquals('/profile/james', self.profile_james.get_absolute_url())

    def test_profile_get_friends_list(self):
        self.profile_james.friends.add(self.profile_vasya.user)
        result = self.profile_james.friends.all()
        expect = self.profile_james.get_friends_list()
        self.assertEquals(list(result), list(expect))

    def test_profile_get_friends_request(self):
        self.relationship = Relationship.objects.create(
            sender=self.profile_vasya,
            receiver=self.profile_james,
            status='send'
        )
        expect = [receiver.sender for receiver in self.profile_james.receiver.all()]
        result = self.profile_james.get_friends_request()
        self.assertEquals(expect, result)

    def test_profile_get_follow_groups(self):
        self.group.followers.add(self.profile_james)
        expect = self.profile_james.follower_groups.all()
        result = self.profile_james.get_follow_groups()
        self.assertEquals(list(expect), list(result))

    def test_profile_get_post_list(self):
        [Post.objects.create(author=self.profile_james, text=f'post number {i}') for i in range(3)]
        expect = self.profile_james.post.all()
        result = self.profile_james.get_post_list()
        self.assertEquals(len(list(expect)), len(list(result)))

