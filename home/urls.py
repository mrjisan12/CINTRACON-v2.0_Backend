from django.urls import path 
from .views import *

urlpatterns = [
    path('post/create', PostCreateView.as_view(), name='post_create'),
    path('post/newsfeed', PostListView.as_view(), name='newsfeed'),
    path('post/comment/<int:post_id>', CommentCreateView.as_view(), name='post_comment'),
    path('post/reaction/<int:post_id>', ReactionCreateView.as_view(), name='post_reaction'),
    path('post/all-comments/<int:post_id>', PostAllCommentsView.as_view(),name="all_comments")
]
