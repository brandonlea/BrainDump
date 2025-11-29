"""
Views for the BrainDump application.

This module handles all user interactions including:
- Viewing and filtering posts
- Creating, editing, and deleting posts
- Adding comments to posts
- Voting on posts (upvote/downvote)
- User authentication (login, logout, register)

All views follow Django best practices with proper error handling,
user feedback, and security considerations.

Author: Brandon-Lea
Date: 2025
Project: BrainDump - Level 5 Diploma Unit 3
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum, Case, When, IntegerField
from .models import Post, Comment, Vote
from .forms import PostForm


def post_list(request):
    """
    Display list of posts with optional category filtering.

    Shows all posts by default, or filters by category if specified in query params.
    Authenticated users can create new posts via this view.

    Args:
        request: HttpRequest object

    Returns:
        HttpResponse with rendered post list template

    Template: posts/post_list.html
    Context:
        - posts: QuerySet of filtered Post objects
        - form: PostForm for creating new posts (authenticated users only)
        - categories: List of available category choices
        - selected_category: Currently selected category filter
        - user_votes: Dictionary mapping post IDs to user's vote values
    """
    # Get category from query parameter
    selected_category = request.GET.get('category', 'everything')

    # Filter posts by category if specified
    if selected_category != 'everything':
        posts = Post.objects.filter(category=selected_category).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')

    # Annotate posts with vote scores
    posts = posts.annotate(
        vote_score=Sum(
            Case(
                When(votes__vote_type=1, then=1),
                When(votes__vote_type=-1, then=-1),
                default=0,
                output_field=IntegerField()
            )
        )
    )

    # Get user's votes for all posts (for displaying vote button states)
    user_votes = {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(user=request.user, post__in=posts)
        user_votes = {vote.post_id: vote.vote_type for vote in votes}

    # Handle post creation (POST request)
    form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                messages.success(request, '🎉 Your thought has been dumped!')
                return redirect('post_list')
        else:
            form = PostForm()

    # Build context
    context = {
        'posts': posts,
        'form': form,
        'categories': dict(Post.CATEGORY_CHOICES),  # ← FIXED: Convert to dictionary
        'selected_category': selected_category,
        'user_votes': user_votes,
    }

    return render(request, 'posts/post_list.html', context)

def post_detail(request, pk):
    """
    Display a single post with all its comments.

    Shows the full post content, voting buttons, comments section,
    and comment form for authenticated users.

    Args:
        request: HTTP request object
        pk (int): Primary key of the post to display

    Returns:
        HttpResponse: Rendered template with post details

    Raises:
        Http404: If post with given pk does not exist

    Template:
        posts/post_detail.html

    Context:
        post: Post object
        comments: QuerySet of Comment objects for this post
        user_vote: User's vote type (1, -1, or None)
        vote_score: Total vote score for this post
    """
    # Get post or return 404 if not found
    # This is better than Post.objects.get() which raises DoesNotExist
    post = get_object_or_404(Post, pk=pk)

    # Get all comments for this post (ordered oldest first)
    comments = post.comments.all()

    # Get user's vote on this post (if any)
    # This is used to highlight the voted button
    user_vote = None
    if request.user.is_authenticated:
        vote = Vote.objects.filter(user=request.user, post=post).first()
        if vote:
            user_vote = vote.vote_type

    # Calculate total vote score for this post
    # Sum all vote_type values (upvotes = +1, downvotes = -1)
    vote_score = post.votes.aggregate(total=Sum('vote_type'))['total'] or 0

    # Prepare context data for template
    context = {
        'post': post,
        'comments': comments,
        'user_vote': user_vote,
        'vote_score': vote_score,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """
    Redirect to home page (post creation happens on main feed).

    This view is kept for URL compatibility but redirects users
    to the main feed where the post creation form is located.

    Args:
        request: HTTP request object

    Returns:
        HttpResponseRedirect: Redirect to post_list
    """
    messages.info(request, 'Create your post from the main feed!')
    return redirect('post_list')


@login_required
def post_edit(request, pk):
    """
    Edit an existing post.

    Only the post author can edit their own posts. Includes
    authorization check to prevent unauthorized editing.

    Args:
        request: HTTP request object
        pk (int): Primary key of the post to edit

    Returns:
        HttpResponse: Rendered edit form or redirect after save

    Security:
        - Requires login (@login_required)
        - Checks if user is the post author

    Template:
        posts/post_form.html

    Context:
        form: PostForm with existing post data
        title: Page title for template
    """
    # Get post or return 404
    post = get_object_or_404(Post, pk=pk)

    # Authorization check: Only author can edit their post
    # This prevents users from editing other people's posts
    if post.author != request.user:
        messages.error(request, "❌ You can only edit your own posts!")
        return redirect('post_detail', pk=pk)

    # Handle form submission
    if request.method == 'POST':
        # Create form with POST data and existing post instance
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Your post has been updated!')
            return redirect('post_detail', pk=pk)
    else:
        # Display form pre-filled with existing post data
        form = PostForm(instance=post)

    # Prepare context for template
    context = {
        'form': form,
        'title': 'Edit Post'
    }

    return render(request, 'posts/post_form.html', context)


@login_required
def post_delete(request, pk):
    """
    Delete a post.

    Only the post author can delete their own posts. Requires
    confirmation via POST request to prevent accidental deletion.

    Args:
        request: HTTP request object
        pk (int): Primary key of the post to delete

    Returns:
        HttpResponse: Confirmation page or redirect after deletion

    Security:
        - Requires login (@login_required)
        - Checks if user is the post author
        - Requires POST request for actual deletion

    Template:
        posts/post_confirm_delete.html

    Context:
        post: Post object to be deleted
    """
    # Get post or return 404
    post = get_object_or_404(Post, pk=pk)

    # Authorization check: Only author can delete their post
    if post.author != request.user:
        messages.error(request, "❌ You can only delete your own posts!")
        return redirect('post_detail', pk=pk)

    # Handle deletion (POST request only for security)
    if request.method == 'POST':
        # Store title for success message before deletion
        post_title = post.title
        post.delete()
        messages.success(request, f'🗑️ "{post_title}" has been deleted.')
        return redirect('post_list')

    # Show confirmation page for GET requests
    return render(request, 'posts/post_confirm_delete.html', {'post': post})


@login_required
def add_comment(request, pk):
    """
    Add a comment to a post.

    Only authenticated users can comment. Validates that comment
    content is not empty before saving.

    Args:
        request: HTTP request object
        pk (int): Primary key of the post to comment on

    Returns:
        HttpResponseRedirect: Redirect back to post detail page

    Security:
        - Requires login (@login_required)
        - Validates comment content presence

    Post Parameters:
        content (str): The comment text
    """
    # Get post or return 404
    post = get_object_or_404(Post, pk=pk)

    # Only process POST requests (comments are submitted via form)
    if request.method == 'POST':
        # Get comment content from form
        content = request.POST.get('content')

        # Validate that content is not empty
        # Django forms handle this, but extra validation for security
        if content and content.strip():
            # Create and save comment
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content.strip()
            )
            messages.success(request, '💬 Your comment has been added!')
        else:
            messages.error(request, '❌ Comment cannot be empty!')

    # Redirect back to post detail page
    return redirect('post_detail', pk=pk)


@login_required
def upvote_post(request, pk):
    """
    Upvote a post from the detail page.

    Voting logic:
    - If user hasn't voted: Create upvote
    - If user already upvoted: Remove vote (toggle off)
    - If user downvoted: Change to upvote

    Users cannot vote on their own posts.

    Args:
        request: HTTP request object
        pk (int): Primary key of the post to upvote

    Returns:
        HttpResponseRedirect: Redirect back to post detail

    Security:
        - Requires login (@login_required)
        - Prevents voting on own posts
    """
    # Get post or return 404
    post = get_object_or_404(Post, pk=pk)

    # Prevent users from voting on their own posts
    # This maintains fairness and prevents vote manipulation
    if post.author == request.user:
        messages.error(request, "❌ You can't vote on your own post!")
        return redirect('post_detail', pk=pk)

    # Check for existing vote by this user on this post
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == 1:
            # User already upvoted - remove the vote (toggle off)
            existing_vote.delete()
            messages.info(request, 'Upvote removed.')
        else:
            # User had downvoted - change to upvote
            existing_vote.vote_type = 1
            existing_vote.save()
            messages.success(request, '👍 Upvoted!')
    else:
        # No existing vote - create new upvote
        Vote.objects.create(user=request.user, post=post, vote_type=1)
        messages.success(request, '👍 Upvoted!')

    return redirect('post_detail', pk=pk)


@login_required
def downvote_post(request, pk):
    """
    Downvote a post from the detail page.

    Voting logic:
    - If user hasn't voted: Create downvote
    - If user already downvoted: Remove vote (toggle off)
    - If user upvoted: Change to downvote

    Users cannot vote on their own posts.

    Args:
        request: HTTP request object
        pk (int): Primary key of the post to downvote

    Returns:
        HttpResponseRedirect: Redirect back to post detail

    Security:
        - Requires login (@login_required)
        - Prevents voting on own posts
    """
    # Get post or return 404
    post = get_object_or_404(Post, pk=pk)

    # Prevent users from voting on their own posts
    if post.author == request.user:
        messages.error(request, "❌ You can't vote on your own post!")
        return redirect('post_detail', pk=pk)

    # Check for existing vote by this user on this post
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == -1:
            # User already downvoted - remove the vote (toggle off)
            existing_vote.delete()
            messages.info(request, 'Downvote removed.')
        else:
            # User had upvoted - change to downvote
            existing_vote.vote_type = -1
            existing_vote.save()
            messages.success(request, '👎 Downvoted!')
    else:
        # No existing vote - create new downvote
        Vote.objects.create(user=request.user, post=post, vote_type=-1)
        messages.success(request, '👎 Downvoted!')

    return redirect('post_detail', pk=pk)


@login_required
def upvote_post_feed(request, pk):
    """
    Upvote a post from the main feed.

    Same voting logic as upvote_post but redirects to feed instead
    of post detail page for better UX on the main feed.

    Args:
        request: HTTP request object
        pk (int): Primary key of the post to upvote

    Returns:
        HttpResponseRedirect: Redirect back to main feed

    Security:
        - Requires login (@login_required)
        - Prevents voting on own posts
    """
    # Get post or return 404
    post = get_object_or_404(Post, pk=pk)

    # Prevent voting on own posts
    if post.author == request.user:
        messages.error(request, "❌ You can't vote on your own post!")
        return redirect('post_list')

    # Check for existing vote
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == 1:
            # Already upvoted - remove vote
            existing_vote.delete()
        else:
            # Was downvote - change to upvote
            existing_vote.vote_type = 1
            existing_vote.save()
    else:
        # Create new upvote
        Vote.objects.create(user=request.user, post=post, vote_type=1)

    return redirect('post_list')


@login_required
def downvote_post_feed(request, pk):
    """
    Downvote a post from the main feed.

    Same voting logic as downvote_post but redirects to feed instead
    of post detail page for better UX on the main feed.

    Args:
        request: HTTP request object
        pk (int): Primary key of the post to downvote

    Returns:
        HttpResponseRedirect: Redirect back to main feed

    Security:
        - Requires login (@login_required)
        - Prevents voting on own posts
    """
    # Get post or return 404
    post = get_object_or_404(Post, pk=pk)

    # Prevent voting on own posts
    if post.author == request.user:
        messages.error(request, "❌ You can't vote on your own post!")
        return redirect('post_list')

    # Check for existing vote
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == -1:
            # Already downvoted - remove vote
            existing_vote.delete()
        else:
            # Was upvote - change to downvote
            existing_vote.vote_type = -1
            existing_vote.save()
    else:
        # Create new downvote
        Vote.objects.create(user=request.user, post=post, vote_type=-1)

    return redirect('post_list')


def register_view(request):
    """
    User registration view.

    Creates a new user account using Django's built-in UserCreationForm.
    Automatically logs in the user after successful registration.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Registration form or redirect after registration

    Template:
        registration/register.html

    Context:
        form: UserCreationForm for user registration
    """
    # Handle form submission
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save new user
            user = form.save()

            # Log in the user automatically after registration
            # This provides better UX - users don't have to log in separately
            login(request, user)

            # Welcome message
            messages.success(
                request,
                f'🎉 Welcome to BrainDump, {user.username}!'
            )
            return redirect('post_list')
    else:
        # Display empty registration form
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """
    Log out the current user.

    Ends the user's session and redirects to the home page.

    Args:
        request: HTTP request object

    Returns:
        HttpResponseRedirect: Redirect to main feed
    """
    # Log out user (clears session)
    logout(request)

    # Show goodbye message
    messages.success(request, '👋 You have been logged out!')

    return redirect('post_list')
