"""
Admin configuration for the BrainDump application.

Customizes the Django admin interface for managing posts, comments,
and votes with enhanced list displays, filters, and search capabilities.

Author: Brandon-Lea
Date: 2025
Project: BrainDump - Level 5 Diploma Unit 3
"""

from django.contrib import admin
from .models import Post, Comment, Vote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Post model.

    Features:
        - List display with key fields
        - Filtering by category, vibe, and date
        - Search by title, content, and author
        - Date hierarchy for easy navigation
    """

    # Fields to display in list view
    list_display = ('title', 'author', 'category', 'vibe', 'created_at')

    # Filters in sidebar
    list_filter = ('category', 'vibe', 'created_at')

    # Search functionality
    search_fields = ('title', 'content', 'author__username')

    # Date hierarchy navigation
    date_hierarchy = 'created_at'

    # Fields to make clickable links in list view
    list_display_links = ('title',)

    # Read-only fields (automatically set)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Comment model.

    Features:
        - List display with author, post, and date
        - Filtering by creation date
        - Search by content, author, and post title
    """

    # Fields to display in list view
    list_display = ('author', 'post', 'created_at')

    # Filters in sidebar
    list_filter = ('created_at',)

    # Search functionality
    search_fields = ('content', 'author__username', 'post__title')

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Vote model.

    Features:
        - List display with user, post/comment, vote type, and date
        - Filtering by vote type and date
        - Search by username and post title
    """

    # Fields to display in list view
    list_display = ('user', 'post', 'comment', 'vote_type', 'created_at')

    # Filters in sidebar
    list_filter = ('vote_type', 'created_at')

    # Search functionality
    search_fields = ('user__username', 'post__title')

    # Read-only fields
    readonly_fields = ('created_at',)
