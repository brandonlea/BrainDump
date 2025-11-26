from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'vibe']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Give your thought a catchy title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Dump your thoughts here...',
                'rows': 6
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'vibe': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Add your comment...',
                'rows': 3
            }),
        }
