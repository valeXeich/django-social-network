def get_posts_for_user(profile):
    """"
     News feed of posts:
     friends, groups
     """
    profile_post = []
    for post in profile.post.select_related('author').prefetch_related('liked', 'disliked', 'comments__author').filter(group=None):
        profile_post.append(post)
    for group in profile.follower_groups.all():
        for post_group in group.group_post.all():
            profile_post.append(post_group)
    for friend in profile.friends.all():
        for post_friend in friend.profile.post.filter(group=None):
            profile_post.append(post_friend)
    sorted_by_date = sorted(profile_post, key=lambda post: post.created_date, reverse=True)
    return sorted_by_date
