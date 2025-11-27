"""
Forms for the BrainDump application.
Defines forms for creating and editing posts and comments.
"""

from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """
    Form for creating and editing posts.
    Includes custom styling for form fields with Tailwind CSS.
    """

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'vibe']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none font-medium text-base',
                'placeholder': 'Give your thought a catchy title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none resize-vertical font-medium text-base',
                'placeholder': "What's on your mind?",
                'rows': 8
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none font-medium text-base'
            }),
            'vibe': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none font-medium text-base'
            }),
        }
        labels = {
            'title': 'Title',
            'content': 'Content',
            'category': 'Category',
            'vibe': 'Vibe',
        }


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to posts.
    """

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none resize-none font-medium',
                'placeholder': 'Add your comment...',
                'rows': 4
            }),
        }
        labels = {
            'content': '',
        }