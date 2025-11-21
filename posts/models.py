from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Post(models.Model):
    CATEGORY_CHOICES = [
        ('oops', 'Oops I did It Again'),
        ('pets', 'Pet Nonsense'),
        ('existential', 'Existential Dread'),
        ('shower', 'Shower Thoughts'),
        ('brain', 'Brain Farts'),
        ('plot', 'Plot Twists'),
    ]

    VIBE_CHOICES = [
        ('chaotic', 'Chaotic'),
        ('silly', 'Silly'),
        ('existential', 'Existential'),
        ('mindblowing', 'Mindblowing'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(max_length=5000)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='shower')
    vibe = models.CharField(max_length=50, choices=VIBE_CHOICES, default='silly')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

class Vote(models.Model):
    VOTE_CHOICES = [
        (1, 'Upvote'),
        (-1, 'Downvote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    vote_type = models.IntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_vote'),
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_comment_vote'),
        ]

    def __str__(self):
        target = self.post if self.post else self.comment
        return f'{self.user.username} voted on {target}'