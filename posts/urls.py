"""
URL configuration for the posts app.
Maps URL patterns to their corresponding views.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Main feed and post creation
    path('', views.post_list, name='post_list'),

    # Post CRUD operations
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),

    # Comments
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),

    # Voting from detail page
    path('post/<int:pk>/upvote/', views.upvote_post, name='upvote_post'),
    path('post/<int:pk>/downvote/', views.downvote_post, name='downvote_post'),

    # Voting from main feed
    path('feed/post/<int:pk>/upvote/', views.upvote_post_feed, name='upvote_post_feed'),
    path('feed/post/<int:pk>/downvote/', views.downvote_post_feed, name='downvote_post_feed'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]