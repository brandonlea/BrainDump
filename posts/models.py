"""
Models for the BrainDump application.
Defines the database structure for posts, comments, and votes.
"""

from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """
    Represents a single post/thought shared by a user.
    Contains the main content along with categorization and metadata.
    """

    # Category choices for organizing posts
    CATEGORY_CHOICES = [
        ('oops', '🤦 Oops I Did It Again'),
        ('pets', '🐾 Pet Nonsense'),
        ('existential', '🤔 Existential Dread'),
        ('shower', '🚿 Shower Thoughts'),
        ('brain', '💨 Brain Farts'),
        ('plot', '🎬 Plot Twists'),
    ]

    # Vibe/mood choices for posts
    VIBE_CHOICES = [
        ('chaotic', '🌪️ Chaotic'),
        ('silly', '🤪 Silly'),
        ('existential', '🤯 Existential'),
        ('mindblowing', '💡 Mindblowing'),
    ]

    # Post fields
    title = models.CharField(max_length=200, help_text="Catchy title for your thought")
    content = models.TextField(max_length=5000, help_text="The full content of your post")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    vibe = models.CharField(max_length=20, choices=VIBE_CHOICES)

    # Relationships
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Newest posts first

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Represents a comment on a post.
    Users can leave comments to engage with posts.
    """

    # Relationships
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    # Comment content
    content = models.TextField(max_length=2000, help_text="Your comment")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']  # Oldest comments first

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


class Vote(models.Model):
    """
    Represents a vote (upvote or downvote) on a post.
    Users can vote on posts to show approval or disapproval.
    """

    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)

    # Vote type: 1 for upvote, -1 for downvote
    vote_type = models.IntegerField(choices=[(1, 'Upvote'), (-1, 'Downvote')])

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can only vote once per post
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_vote'),
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_comment_vote'),
        ]

    def __str__(self):
        vote_str = "Upvote" if self.vote_type == 1 else "Downvote"
        if self.post:
            return f'{vote_str} by {self.user.username} on post {self.post.title}'
        return f'{vote_str} by {self.user.username} on comment'