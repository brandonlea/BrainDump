"""
Views for the BrainDump application.
Handles all user interactions including viewing, creating, editing posts,
commenting, and voting functionality.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Post, Comment, Vote
from .forms import PostForm, CommentForm


def post_list(request):
    """
    Display the main feed with all posts.
    Includes post creation form for authenticated users.
    Allows filtering by category and shows voting options.
    """
    # Get all posts
    posts = Post.objects.all()

    # Filter by category if provided in URL parameters
    category = request.GET.get('category')
    if category and category != 'everything':
        posts = posts.filter(category=category)

    # Annotate posts with vote scores (sum of all vote_type values)
    posts = posts.annotate(vote_score=Sum('votes__vote_type'))

    # Get user's votes for highlighting voted posts
    user_votes = {}
    if request.user.is_authenticated:
        user_vote_objs = Vote.objects.filter(user=request.user, post__in=posts)
        user_votes = {vote.post_id: vote.vote_type for vote in user_vote_objs}

    # Handle post creation form submission
    if request.method == 'POST' and request.user.is_authenticated:
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '🎉 Your thought has been dumped into the void!')
            return redirect('post_list')
    else:
        form = PostForm()

    # Get category choices for sidebar
    categories = Post.CATEGORY_CHOICES

    context = {
        'posts': posts,
        'categories': categories,
        'selected_category': category or 'everything',
        'form': form,
        'user_votes': user_votes,
    }
    return render(request, 'posts/post_list.html', context)


def post_detail(request, pk):
    """
    Display a single post with all its comments.
    Shows voting buttons and allows adding comments.
    """
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()

    # Get user's vote on this post
    user_vote = None
    if request.user.is_authenticated:
        vote = Vote.objects.filter(user=request.user, post=post).first()
        if vote:
            user_vote = vote.vote_type

    # Calculate vote score
    vote_score = post.votes.aggregate(total=Sum('vote_type'))['total'] or 0

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
    Redirect to home page since post creation happens on main feed.
    This view is kept for URL compatibility but not used.
    """
    messages.info(request, 'Create your post from the main feed!')
    return redirect('post_list')


@login_required
def post_edit(request, pk):
    """
    Edit an existing post.
    Only the author can edit their own posts.
    """
    post = get_object_or_404(Post, pk=pk)

    # Check if user is the author
    if post.author != request.user:
        messages.error(request, "You can only edit your own posts!")
        return redirect('post_detail', pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Your post has been updated!')
            return redirect('post_detail', pk=pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/post_form.html', {'form': form, 'title': 'Edit Post'})


@login_required
def post_delete(request, pk):
    """
    Delete a post.
    Only the author can delete their own posts.
    Requires confirmation via POST request.
    """
    post = get_object_or_404(Post, pk=pk)

    # Check if user is the author
    if post.author != request.user:
        messages.error(request, "You can only delete your own posts!")
        return redirect('post_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, '🗑️ Your post has been deleted.')
        return redirect('post_list')

    return render(request, 'posts/post_confirm_delete.html', {'post': post})


@login_required
def add_comment(request, pk):
    """
    Add a comment to a post.
    Only authenticated users can comment.
    """
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            messages.success(request, '💬 Your comment has been added!')
        else:
            messages.error(request, 'Comment cannot be empty!')

    return redirect('post_detail', pk=pk)


@login_required
def upvote_post(request, pk):
    """
    Upvote a post from the detail page.
    Users cannot vote on their own posts.
    Clicking upvote again removes the vote.
    """
    post = get_object_or_404(Post, pk=pk)

    # Prevent voting on own post
    if post.author == request.user:
        messages.error(request, "You can't vote on your own post!")
        return redirect('post_detail', pk=pk)

    # Check for existing vote
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == 1:
            # Already upvoted - remove the vote
            existing_vote.delete()
            messages.info(request, 'Upvote removed.')
        else:
            # Was downvote - change to upvote
            existing_vote.vote_type = 1
            existing_vote.save()
            messages.success(request, '👍 Upvoted!')
    else:
        # Create new upvote
        Vote.objects.create(user=request.user, post=post, vote_type=1)
        messages.success(request, '👍 Upvoted!')

    return redirect('post_detail', pk=pk)


@login_required
def downvote_post(request, pk):
    """
    Downvote a post from the detail page.
    Users cannot vote on their own posts.
    Clicking downvote again removes the vote.
    """
    post = get_object_or_404(Post, pk=pk)

    # Prevent voting on own post
    if post.author == request.user:
        messages.error(request, "You can't vote on your own post!")
        return redirect('post_detail', pk=pk)

    # Check for existing vote
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == -1:
            # Already downvoted - remove the vote
            existing_vote.delete()
            messages.info(request, 'Downvote removed.')
        else:
            # Was upvote - change to downvote
            existing_vote.vote_type = -1
            existing_vote.save()
            messages.success(request, '👎 Downvoted!')
    else:
        # Create new downvote
        Vote.objects.create(user=request.user, post=post, vote_type=-1)
        messages.success(request, '👎 Downvoted!')

    return redirect('post_detail', pk=pk)


@login_required
def upvote_post_feed(request, pk):
    """
    Upvote a post from the main feed.
    Returns to the feed after voting.
    """
    post = get_object_or_404(Post, pk=pk)

    # Prevent voting on own post
    if post.author == request.user:
        messages.error(request, "You can't vote on your own post!")
        return redirect('post_list')

    # Check for existing vote
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == 1:
            # Already upvoted - remove the vote
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
    Returns to the feed after voting.
    """
    post = get_object_or_404(Post, pk=pk)

    # Prevent voting on own post
    if post.author == request.user:
        messages.error(request, "You can't vote on your own post!")
        return redirect('post_list')

    # Check for existing vote
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == -1:
            # Already downvoted - remove the vote
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
    Creates a new user account and logs them in automatically.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'🎉 Welcome to BrainDump, {user.username}!')
            return redirect('post_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """
    Log out the current user and redirect to home page.
    """
    logout(request)
    messages.success(request, '👋 You have been logged out!')
    return redirect('post_list')