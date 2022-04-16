def get_posts_for_user(profile):
    profile_post = []
    for post in profile.post.filter(group=None):
        profile_post.append(post)
    for group in profile.follower_groups.all():
        for post_group in group.group_post.all():
            profile_post.append(post_group)
    for friend in profile.friends.all():
        for post_friend in friend.profile.post.filter(group=None):
            profile_post.append(post_friend)
    sorted_by_date = sorted(profile_post, key=lambda post: post.created_date, reverse=True)
    generator = (post for post in sorted_by_date)
    return generator
