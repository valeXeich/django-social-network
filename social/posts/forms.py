from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'image', 'video']

        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write something...'}),
            'image': forms.FileInput(attrs={'type': 'file', 'class': 'fileContainer'}),
            'video': forms.FileInput(attrs={'type': 'file', 'class': 'fileContainer'})}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Write a comment'})}
