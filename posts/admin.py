"""
Admin configuration for the BrainDump application.
Customizes the Django admin interface for managing posts, comments, and votes.
"""

from django.contrib import admin
from .models import Post, Comment, Vote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin interface for Post model.
    Shows key information and provides filtering/search capabilities.
    """
    list_display = ('title', 'author', 'category', 'vibe', 'created_at')
    list_filter = ('category', 'vibe', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model.
    Shows comment details with filtering by post and author.
    """
    list_display = ('author', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__title')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """
    Admin interface for Vote model.
    Shows voting activity with user and vote type information.
    """
    list_display = ('user', 'post', 'comment', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at')
    search_fields = ('user__username', 'post__title')