import vimeo
import requests

from config.vimeo_data import token, key, secret
from config.celery import app

from .models import Post

client = vimeo.VimeoClient(
    token=token,
    key=key,
    secret=secret
)

@app.task
def upload_to_vimeo(file_path, profile_slug, text, post_id):
    """"Task for uploading video to vimeo"""
    post = Post.objects.get(id=post_id)
    uri = client.upload(file_path, data={
        'name': f'Video by {profile_slug}',
        'description': text
    })
    video_id = uri.split('/')[-1]
    post.vimeo_url = f'https://player.vimeo.com/video/{video_id}'
    post.save()

@app.task
def delete_video_from_vimeo(vimeo_id):
    """"Task to delete a video on vimeo"""
    url = f'https://api.vimeo.com/videos/{vimeo_id}'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    return requests.delete(url, headers=headers)

