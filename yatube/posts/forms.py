from django import forms
from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        widgets = {
            "text": forms.Textarea(attrs={"rows": 10, "cols": 40}),
        }
        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
            "image": "Картинка",
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"rows": 10, "cols": 40}),
        }
        help_texts = {
            "text": "Текст нового комментария",
        }
