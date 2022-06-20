from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма добавления/редактирования постов"""
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
            }),
            'group': forms.Select(attrs={
                'class': 'form-control',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }


class CommentForm(forms.ModelForm):
    """Форма для комментирования постов"""
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }
