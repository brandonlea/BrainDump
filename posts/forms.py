"""
Forms for the BrainDump application.

Defines forms for creating and editing posts and comments with
custom styling and validation.

Author: Brandon-Lea
Date: 2025
Project: BrainDump - Level 5 Diploma Unit 3
"""

from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """
    Form for creating and editing posts.

    Includes custom Tailwind CSS styling for all form fields to match
    the application's design. All fields are required and have
    appropriate placeholders for better UX.

    Fields:
        title: Post title (max 200 characters)
        content: Post content (max 5000 characters)
        category: Post category selection
        vibe: Post vibe/mood selection
    """

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'vibe']

        # Custom widgets with Tailwind CSS classes
        widgets = {
            'title': forms.TextInput(attrs={
                'class': (
                    'w-full px-4 py-3 border-2 border-gray-300 '
                    'rounded-lg focus:border-purple-500 '
                    'focus:outline-none font-medium text-base'
                ),
                'placeholder': 'Give your thought a catchy title...'
            }),
            'content': forms.Textarea(attrs={
                'class': (
                    'w-full px-4 py-3 border-2 border-gray-300 '
                    'rounded-lg focus:border-purple-500 '
                    'focus:outline-none resize-vertical font-medium text-base'
                ),
                'placeholder': "What's on your mind?",
                'rows': 8
            }),
            'category': forms.Select(attrs={
                'class': (
                    'w-full px-4 py-3 border-2 border-gray-300 '
                    'rounded-lg focus:border-purple-500 '
                    'focus:outline-none font-medium text-base'
                )
            }),
            'vibe': forms.Select(attrs={
                'class': (
                    'w-full px-4 py-3 border-2 border-gray-300 '
                    'rounded-lg focus:border-purple-500 '
                    'focus:outline-none font-medium text-base'
                )
            }),
        }

        # Custom field labels
        labels = {
            'title': 'Title',
            'content': 'Content',
            'category': 'Category',
            'vibe': 'Vibe',
        }


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to posts.

    Simple form with just a content field. Styled to match the
    application's design with Tailwind CSS.

    Fields:
        content: Comment text (max 2000 characters)
    """

    class Meta:
        model = Comment
        fields = ['content']

        # Custom widget with Tailwind CSS classes
        widgets = {
            'content': forms.Textarea(attrs={
                'class': (
                    'w-full px-4 py-3 border-2 border-gray-300 '
                    'rounded-lg focus:border-purple-500 '
                    'focus:outline-none resize-none font-medium'
                ),
                'placeholder': 'Add your comment...',
                'rows': 4
            }),
        }

        # No label needed (placeholder provides context)
        labels = {
            'content': '',
        }
