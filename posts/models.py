"""
Database models for the BrainDump application.

This module defines the core data structures for the application:
- Post: User-created posts with category and vibe classification
- Comment: Comments on posts for user engagement
- Vote: Upvote/downvote system for posts

Author: Brandon-Lea
Date: 2025
Project: BrainDump - Level 5 Diploma Unit 3
"""

from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """
    Represents a single post/thought shared by a user.

    Posts are the main content type in BrainDump, where users share their
    thoughts, stories, and ideas. Each post is categorized by type and vibe
    to help users filter and discover content.

    Attributes:
        title (str): The post title (max 200 characters)
        content (str): The full post content (max 5000 characters)
        category (str): Post category from predefined choices
        vibe (str): Post mood/vibe from predefined choices
        author (User): The user who created the post
        created_at (datetime): Timestamp when post was created
        updated_at (datetime): Timestamp when post was last modified

    Relationships:
        - Many-to-One with User (author)
        - One-to-Many with Comment
        - One-to-Many with Vote
    """

    # Category choices for organizing posts by topic
    CATEGORY_CHOICES = [
        ('oops', '🤦 Oops I Did It Again'),
        ('pets', '🐾 Pet Nonsense'),
        ('existential', '🤔 Existential Dread'),
        ('shower', '🚿 Shower Thoughts'),
        ('brain', '💨 Brain Farts'),
        ('plot', '🎬 Plot Twists'),
    ]

    # Vibe/mood choices for posts to express emotional tone
    VIBE_CHOICES = [
        ('chaotic', '🌪️ Chaotic'),
        ('silly', '🤪 Silly'),
        ('existential', '🤯 Existential'),
        ('mindblowing', '💡 Mindblowing'),
    ]

    # Core post fields
    title = models.CharField(
        max_length=200,
        help_text="Catchy title for your thought"
    )

    content = models.TextField(
        max_length=5000,
        help_text="The full content of your post"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Category to organize your post"
    )

    vibe = models.CharField(
        max_length=20,
        choices=VIBE_CHOICES,
        help_text="The mood or vibe of your post"
    )

    # Relationship to User model
    # CASCADE ensures posts are deleted when user is deleted
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="The user who created this post"
    )

    # Automatic timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this post was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this post was last updated"
    )

    class Meta:
        """Meta options for Post model."""
        ordering = ['-created_at']  # Newest posts first
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        """
        String representation of the Post.

        Returns:
            str: The post title
        """
        return self.title

    def get_vote_count(self):
        """
        Calculate total vote score for this post.

        Vote score is calculated as the sum of all vote_type values:
        - Each upvote adds +1
        - Each downvote adds -1

        Returns:
            int: The total vote score (can be negative)
        """
        from django.db.models import Sum
        total = self.votes.aggregate(total=Sum('vote_type'))['total']
        return total or 0


class Comment(models.Model):
    """
    Represents a comment on a post.

    Comments allow users to engage with posts by leaving feedback,
    asking questions, or contributing to the discussion.

    Attributes:
        post (Post): The post this comment belongs to
        author (User): The user who wrote the comment
        content (str): The comment text (max 2000 characters)
        created_at (datetime): When the comment was created
        updated_at (datetime): When the comment was last modified

    Relationships:
        - Many-to-One with Post
        - Many-to-One with User (author)
        - One-to-Many with Vote (future feature)
    """

    # Relationship to Post model
    # CASCADE ensures comments are deleted when post is deleted
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The post this comment belongs to"
    )

    # Relationship to User model
    # CASCADE ensures comments are deleted when user is deleted
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The user who wrote this comment"
    )

    # Comment content field
    content = models.TextField(
        max_length=2000,
        help_text="Your comment text"
    )

    # Automatic timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this comment was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this comment was last updated"
    )

    class Meta:
        """Meta options for Comment model."""
        ordering = ['created_at']  # Oldest comments first (chronological)
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        """
        String representation of the Comment.

        Returns:
            str: Brief description of the comment
        """
        return f'Comment by {self.author.username} on {self.post.title}'


class Vote(models.Model):
    """
    Represents a vote (upvote or downvote) on a post.

    Users can vote on posts to show approval (upvote = +1) or
    disapproval (downvote = -1). Each user can only vote once per post,
    but can change their vote or remove it.

    Attributes:
        user (User): The user who cast the vote
        post (Post): The post being voted on (nullable for future comment votes)
        comment (Comment): The comment being voted on (nullable, future feature)
        vote_type (int): 1 for upvote, -1 for downvote
        created_at (datetime): When the vote was cast

    Constraints:
        - unique_post_vote: One vote per user per post
        - unique_comment_vote: One vote per user per comment

    Relationships:
        - Many-to-One with User
        - Many-to-One with Post (optional)
        - Many-to-One with Comment (optional)
    """

    # Vote type choices
    VOTE_CHOICES = [
        (1, 'Upvote'),
        (-1, 'Downvote'),
    ]

    # Relationship to User model
    # CASCADE ensures votes are deleted when user is deleted
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes',
        help_text="The user who cast this vote"
    )

    # Relationship to Post model (nullable for future comment voting)
    # CASCADE ensures votes are deleted when post is deleted
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='votes',
        null=True,
        blank=True,
        help_text="The post being voted on"
    )

    # Relationship to Comment model (future feature)
    # CASCADE ensures votes are deleted when comment is deleted
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='votes',
        null=True,
        blank=True,
        help_text="The comment being voted on (future feature)"
    )

    # Vote type: 1 for upvote, -1 for downvote
    vote_type = models.IntegerField(
        choices=VOTE_CHOICES,
        help_text="1 for upvote, -1 for downvote"
    )

    # Timestamp when vote was cast
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this vote was cast"
    )

    class Meta:
        """
        Meta options for Vote model.

        Ensures each user can only vote once per post or comment
        using database-level constraints for data integrity.
        """
        # Ensure a user can only vote once per post
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_post_vote'
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_comment_vote'
            ),
        ]
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'

    def __str__(self):
        """
        String representation of the Vote.

        Returns:
            str: Description of the vote
        """
        vote_str = "Upvote" if self.vote_type == 1 else "Downvote"
        if self.post:
            return f'{vote_str} by {self.user.username} on "{self.post.title}"'
        return f'{vote_str} by {self.user.username}'
