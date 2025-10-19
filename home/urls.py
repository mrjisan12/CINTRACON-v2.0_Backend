from django.urls import path 
from .views import *

urlpatterns = [
    path('post/create', PostCreateView.as_view(), name='post_create'),
    path('newsfeed', PostListView.as_view(), name='newsfeed'),
    path('post/details/<int:post_id>', PostDetailView.as_view(), name='post_details'),
    path('post/comment/<int:post_id>', CommentCreateView.as_view(), name='post_comment'),
    path('post/reaction/<int:post_id>', ReactionCreateView.as_view(), name='post_reaction'),
    path('post/all-comments/<int:post_id>', PostAllCommentsView.as_view(),name="all_comments"),
    path('right-sidebar-info', RightSidebarInfoView.as_view(), name='right_sidebar_info'),
    path('navbar-info', NavBarInfoView.as_view(), name='nav_bar_info'),
    path('developers', DeveloperListView.as_view(), name='developers_list'),
]
