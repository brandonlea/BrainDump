"""
Tests for BrainDump.

Testing:
- Models (Post, Comment, Vote)
- Views (CRUD, voting, commenting)
- Forms (PostForm, CommentForm)
- Authentication (login, logout, registration, permissions)

Author: Brandon-Lea
Date: 2025
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
from .models import Post, Comment, Vote
from .forms import PostForm, CommentForm


# =============================================================================
# MODEL TESTS
# =============================================================================

class PostModelTest(TestCase):
    """Tests for the Post model."""

    @classmethod
    def setUpTestData(cls):
        """Create test data that persists across all test methods."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            category='oops',
            vibe='chaotic',
            author=cls.user
        )

    def test_post_creation(self):
        """Post should be created with all fields set correctly."""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post content.')
        self.assertEqual(self.post.category, 'oops')
        self.assertEqual(self.post.vibe, 'chaotic')
        self.assertEqual(self.post.author, self.user)

    def test_post_str_method(self):
        """Test the string representation of Post model."""
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_ordering(self):
        """Test that posts are ordered by newest first."""
        post2 = Post.objects.create(
            title='Newer Post',
            content='Content',
            category='shower',
            vibe='silly',
            author=self.user
        )
        posts = list(Post.objects.all())
        self.assertEqual(posts[0], post2)  # Newer post should be first
        self.assertEqual(posts[1], self.post)

    def test_get_vote_count_no_votes(self):
        """Vote count should be 0 when no votes exist."""
        self.assertEqual(self.post.get_vote_count(), 0)

    def test_get_vote_count_with_votes(self):
        """Vote count should sum upvotes and downvotes correctly."""
        user2 = User.objects.create_user(username='voter1', password='pass')
        user3 = User.objects.create_user(username='voter2', password='pass')
        user4 = User.objects.create_user(username='voter3', password='pass')

        # Create votes: +1, +1, -1 = net score of 1
        Vote.objects.create(user=user2, post=self.post, vote_type=1)
        Vote.objects.create(user=user3, post=self.post, vote_type=1)
        Vote.objects.create(user=user4, post=self.post, vote_type=-1)

        self.assertEqual(self.post.get_vote_count(), 1)

    def test_post_deletion_cascades_to_comments(self):
        """Test that deleting a post also deletes associated comments."""
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.assertEqual(Comment.objects.count(), 1)

        self.post.delete()
        self.assertEqual(Comment.objects.count(), 0)

    def test_post_deletion_cascades_to_votes(self):
        """Test that deleting a post also deletes associated votes."""
        user2 = User.objects.create_user(username='voter', password='pass')
        Vote.objects.create(user=user2, post=self.post, vote_type=1)
        self.assertEqual(Vote.objects.count(), 1)

        self.post.delete()
        self.assertEqual(Vote.objects.count(), 0)


class CommentModelTest(TestCase):
    """Tests for Comment model."""

    @classmethod
    def setUpTestData(cls):
        """Create test data for comment tests."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.post = Post.objects.create(
            title='Test Post',
            content='Content',
            category='pets',
            vibe='silly',
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            content='This is a test comment.'
        )

    def test_comment_creation(self):
        """Test that a comment can be created with required fields."""
        self.assertEqual(self.comment.content, 'This is a test comment.')
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.user)

    def test_comment_str_method(self):
        """Test the string representation of Comment model."""
        expected = f'Comment by {self.user.username} on {self.post.title}'
        self.assertEqual(str(self.comment), expected)

    def test_comment_ordering(self):
        """Test that comments are ordered oldest first (chronological)."""
        comment2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Newer comment'
        )
        comments = list(self.post.comments.all())
        self.assertEqual(comments[0], self.comment)  # Older first
        self.assertEqual(comments[1], comment2)


class VoteModelTest(TestCase):
    """Tests for Vote model and constraints."""

    @classmethod
    def setUpTestData(cls):
        """Create test data for vote tests."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.user2 = User.objects.create_user(
            username='voter',
            password='testpass123'
        )
        cls.post = Post.objects.create(
            title='Test Post',
            content='Content',
            category='existential',
            vibe='mindblowing',
            author=cls.user
        )

    def test_upvote_creation(self):
        """Test that an upvote can be created."""
        vote = Vote.objects.create(
            user=self.user2,
            post=self.post,
            vote_type=1
        )
        self.assertEqual(vote.vote_type, 1)
        self.assertEqual(vote.user, self.user2)
        self.assertEqual(vote.post, self.post)

    def test_downvote_creation(self):
        """Test that a downvote can be created."""
        vote = Vote.objects.create(
            user=self.user2,
            post=self.post,
            vote_type=-1
        )
        self.assertEqual(vote.vote_type, -1)

    def test_unique_vote_constraint(self):
        """User shouldn't be able to vote twice on same post."""
        Vote.objects.create(
            user=self.user2,
            post=self.post,
            vote_type=1
        )

        # Attempting to create second vote should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Vote.objects.create(
                user=self.user2,
                post=self.post,
                vote_type=1
            )

    def test_vote_str_method(self):
        """Test the string representation of Vote model."""
        vote = Vote.objects.create(
            user=self.user2,
            post=self.post,
            vote_type=1
        )
        expected = f'Upvote by {self.user2.username} on "{self.post.title}"'
        self.assertEqual(str(vote), expected)

    def test_vote_deletion_when_user_deleted(self):
        """Test that votes are deleted when user is deleted (CASCADE)."""
        Vote.objects.create(
            user=self.user2,
            post=self.post,
            vote_type=1
        )
        self.assertEqual(Vote.objects.count(), 1)

        self.user2.delete()
        self.assertEqual(Vote.objects.count(), 0)


# =============================================================================
# VIEW TESTS
# =============================================================================

class PostListViewTest(TestCase):
    """
    Test suite for the post_list view.

    Tests:
    - View accessible and uses correct template
    - Category filtering functionality
    - Post display and ordering
    - Form display for authenticated users
    """

    def setUp(self):
        """Create test data and client for each test."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post1 = Post.objects.create(
            title='First Post',
            content='Content 1',
            category='oops',
            vibe='chaotic',
            author=self.user
        )
        self.post2 = Post.objects.create(
            title='Second Post',
            content='Content 2',
            category='pets',
            vibe='silly',
            author=self.user
        )

    def test_post_list_view_accessible(self):
        """Test that post list view is accessible and returns 200."""
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)

    def test_post_list_uses_correct_template(self):
        """Test that post list view uses the correct template."""
        response = self.client.get(reverse('post_list'))
        self.assertTemplateUsed(response, 'posts/post_list.html')

    def test_post_list_shows_all_posts_by_default(self):
        """Test that all posts are shown when no category filter applied."""
        response = self.client.get(reverse('post_list'))
        self.assertEqual(len(response.context['posts']), 2)

    def test_post_list_category_filtering(self):
        """Test that category filtering works correctly."""
        response = self.client.get(reverse('post_list') + '?category=oops')
        posts = list(response.context['posts'])
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, 'First Post')

    def test_post_list_form_not_shown_when_logged_out(self):
        """Test that post creation form is not shown to logged-out users."""
        response = self.client.get(reverse('post_list'))
        self.assertIsNone(response.context['form'])

    def test_post_list_form_shown_when_logged_in(self):
        """Test that post creation form is shown to authenticated users."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('post_list'))
        self.assertIsNotNone(response.context['form'])


class PostDetailViewTest(TestCase):
    """
    Test suite for the post_detail view.

    Tests:
    - View accessible with valid post ID
    - 404 for non-existent posts
    - Comments displayed correctly
    - Vote score calculated correctly
    """

    def setUp(self):
        """Create test data for post detail tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Content',
            category='shower',
            vibe='mindblowing',
            author=self.user
        )

    def test_post_detail_view_accessible(self):
        """Test that post detail view is accessible with valid ID."""
        response = self.client.get(
            reverse('post_detail', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_post_detail_view_404_for_invalid_id(self):
        """Test that post detail view returns 404 for non-existent post."""
        response = self.client.get(
            reverse('post_detail', kwargs={'pk': 9999})
        )
        self.assertEqual(response.status_code, 404)

    def test_post_detail_uses_correct_template(self):
        """Test that post detail view uses correct template."""
        response = self.client.get(
            reverse('post_detail', kwargs={'pk': self.post.pk})
        )
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_post_detail_shows_comments(self):
        """Test that comments are displayed on post detail page."""
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        response = self.client.get(
            reverse('post_detail', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(len(response.context['comments']), 1)


class PostCRUDTest(TestCase):
    """
    Test suite for Post CRUD operations.

    Tests:
    - Creating posts (requires login)
    - Editing posts (only author)
    - Deleting posts (only author)
    - Authorization checks
    """

    def setUp(self):
        """Create test users and posts."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Content',
            category='brain',
            vibe='chaotic',
            author=self.user
        )

    def test_create_post_requires_login(self):
        """Test that creating a post requires authentication."""
        response = self.client.post(reverse('post_list'), {
            'title': 'New Post',
            'content': 'New content',
            'category': 'oops',
            'vibe': 'silly'
        })
        # Should not create post
        self.assertEqual(Post.objects.count(), 1)  # Still just the setup post

    def test_create_post_when_logged_in(self):
        """Test that authenticated user can create a post."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('post_list'), {
            'title': 'New Post',
            'content': 'New content',
            'category': 'oops',
            'vibe': 'silly'
        })
        self.assertEqual(Post.objects.count(), 2)
        new_post = Post.objects.latest('created_at')
        self.assertEqual(new_post.title, 'New Post')
        self.assertEqual(new_post.author, self.user)

    def test_edit_post_requires_login(self):
        """Test that editing a post requires authentication."""
        response = self.client.get(
            reverse('post_edit', kwargs={'pk': self.post.pk})
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_edit_own_post(self):
        """Test that post author can edit their own post."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('post_edit', kwargs={'pk': self.post.pk}),
            {
                'title': 'Updated Title',
                'content': 'Updated content',
                'category': 'oops',
                'vibe': 'silly'
            }
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_cannot_edit_other_user_post(self):
        """Test that users cannot edit posts by other users."""
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.post(
            reverse('post_edit', kwargs={'pk': self.post.pk}),
            {
                'title': 'Hacked Title',
                'content': 'Hacked content',
                'category': 'oops',
                'vibe': 'silly'
            }
        )
        self.post.refresh_from_db()
        # Title should remain unchanged
        self.assertEqual(self.post.title, 'Test Post')

    def test_delete_own_post(self):
        """Test that post author can delete their own post."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('post_delete', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_cannot_delete_other_user_post(self):
        """Test that users cannot delete posts by other users."""
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.post(
            reverse('post_delete', kwargs={'pk': self.post.pk})
        )
        # Post should still exist
        self.assertEqual(Post.objects.count(), 1)


class VotingTest(TestCase):
    """
    Test suite for voting functionality.

    Tests:
    - Upvoting and downvoting posts
    - Removing votes (toggle)
    - Changing votes
    - Cannot vote on own posts
    - Login required for voting
    """

    def setUp(self):
        """Create test users and post for voting tests."""
        self.client = Client()
        self.author = User.objects.create_user(
            username='author',
            password='testpass123'
        )
        self.voter = User.objects.create_user(
            username='voter',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Content',
            category='plot',
            vibe='mindblowing',
            author=self.author
        )

    def test_upvote_requires_login(self):
        """Test that voting requires authentication."""
        response = self.client.post(
            reverse('upvote_post', kwargs={'pk': self.post.pk})
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vote.objects.count(), 0)

    def test_upvote_post(self):
        """Test that authenticated user can upvote a post."""
        self.client.login(username='voter', password='testpass123')
        response = self.client.post(
            reverse('upvote_post', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(Vote.objects.count(), 1)
        vote = Vote.objects.first()
        self.assertEqual(vote.vote_type, 1)
        self.assertEqual(vote.user, self.voter)

    def test_downvote_post(self):
        """Test that authenticated user can downvote a post."""
        self.client.login(username='voter', password='testpass123')
        response = self.client.post(
            reverse('downvote_post', kwargs={'pk': self.post.pk})
        )
        self.assertEqual(Vote.objects.count(), 1)
        vote = Vote.objects.first()
        self.assertEqual(vote.vote_type, -1)

    def test_toggle_upvote_off(self):
        """Test that clicking upvote again removes the vote."""
        self.client.login(username='voter', password='testpass123')
        # First upvote
        self.client.post(reverse('upvote_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(Vote.objects.count(), 1)

        # Second upvote (toggle off)
        self.client.post(reverse('upvote_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(Vote.objects.count(), 0)

    def test_change_vote_from_upvote_to_downvote(self):
        """Test that user can change their vote from upvote to downvote."""
        self.client.login(username='voter', password='testpass123')
        # First upvote
        self.client.post(reverse('upvote_post', kwargs={'pk': self.post.pk}))
        vote = Vote.objects.first()
        self.assertEqual(vote.vote_type, 1)

        # Change to downvote
        self.client.post(reverse('downvote_post', kwargs={'pk': self.post.pk}))
        vote.refresh_from_db()
        self.assertEqual(vote.vote_type, -1)
        self.assertEqual(Vote.objects.count(), 1)  # Still one vote

    def test_cannot_vote_on_own_post(self):
        """Test that users cannot vote on their own posts."""
        self.client.login(username='author', password='testpass123')
        response = self.client.post(
            reverse('upvote_post', kwargs={'pk': self.post.pk})
        )
        # Vote should not be created
        self.assertEqual(Vote.objects.count(), 0)


class CommentTest(TestCase):
    """
    Test suite for commenting functionality.

    Tests:
    - Adding comments (requires login)
    - Empty comment validation
    - Comment display
    """

    def setUp(self):
        """Create test data for comment tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Content',
            category='oops',
            vibe='chaotic',
            author=self.user
        )

    def test_add_comment_requires_login(self):
        """Test that adding a comment requires authentication."""
        response = self.client.post(
            reverse('add_comment', kwargs={'pk': self.post.pk}),
            {'content': 'Test comment'}
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)

    def test_add_comment_when_logged_in(self):
        """Test that authenticated user can add a comment."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('add_comment', kwargs={'pk': self.post.pk}),
            {'content': 'This is a great post!'}
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'This is a great post!')
        self.assertEqual(comment.author, self.user)

    def test_empty_comment_not_created(self):
        """Test that empty comments are not created."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('add_comment', kwargs={'pk': self.post.pk}),
            {'content': '   '}  # Only whitespace
        )
        self.assertEqual(Comment.objects.count(), 0)


# =============================================================================
# FORM TESTS
# =============================================================================

class PostFormTest(TestCase):
    """
    Test suite for PostForm validation.

    Tests:
    - Valid form data
    - Required fields
    - Invalid category/vibe choices
    - Max length enforcement
    """

    def test_valid_post_form(self):
        """Test that PostForm validates with correct data."""
        form_data = {
            'title': 'Test Post',
            'content': 'This is test content.',
            'category': 'oops',
            'vibe': 'chaotic'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_missing_required_fields(self):
        """Test that PostForm is invalid when required fields are missing."""
        form = PostForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)  # All 4 fields required

    def test_post_form_invalid_category(self):
        """Test that PostForm rejects invalid category choices."""
        form_data = {
            'title': 'Test Post',
            'content': 'Content',
            'category': 'invalid_category',
            'vibe': 'chaotic'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_post_form_title_max_length(self):
        """Test that PostForm enforces title max length."""
        form_data = {
            'title': 'x' * 201,  # Exceeds max length of 200
            'content': 'Content',
            'category': 'oops',
            'vibe': 'silly'
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())


class CommentFormTest(TestCase):
    """
    Test suite for CommentForm validation.

    Tests:
    - Valid form data
    - Required content field
    - Max length enforcement
    """

    def test_valid_comment_form(self):
        """Test that CommentForm validates with correct data."""
        form_data = {'content': 'This is a test comment.'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_missing_content(self):
        """Test that CommentForm is invalid when content is missing."""
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_comment_form_max_length(self):
        """Test that CommentForm enforces content max length."""
        form_data = {'content': 'x' * 2001}  # Exceeds max length of 2000
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

class AuthenticationTest(TestCase):
    """
    Test suite for user authentication.

    Tests:
    - User registration
    - User login
    - User logout
    - Auto-login after registration
    """

    def setUp(self):
        """Create test client."""
        self.client = Client()

    def test_user_registration(self):
        """Test that user can register a new account."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        })
        # User should be created
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, 'newuser')

    def test_user_login(self):
        """Test that user can log in with correct credentials."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Check that user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_logout(self):
        """Test that user can log out."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(reverse('logout'))

        # Check that user is logged out
        response = self.client.get(reverse('post_list'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_auto_login_after_registration(self):
        """Test that user is automatically logged in after registration."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }, follow=True)
        # User should be logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'newuser')
