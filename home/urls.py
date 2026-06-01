from django.urls import path 
from .views import *

urlpatterns = [
    path('post/create', PostCreateView.as_view(), name='post_create'),
    path('post/update/<int:post_id>', PostEditView.as_view(), name='post_edit'),
    path('post/delete/<int:post_id>', PostDeleteView.as_view(), name='post_delete'),
    path('newsfeed', PostListView.as_view(), name='newsfeed'),
    path('post/details/<int:post_id>', PostDetailView.as_view(), name='post_details'),
    path('post/comment/<int:post_id>', CommentCreateView.as_view(), name='post_comment'),
    path('post/reaction/<int:post_id>', ReactionCreateView.as_view(), name='post_reaction'),
    path('post/all-comments/<int:post_id>', PostAllCommentsView.as_view(),name="all_comments"),
    path('post/report/<int:post_id>', ReportCreateView.as_view(), name='post_report'),
    path('right-sidebar-info', RightSidebarInfoView.as_view(), name='right_sidebar_info'),
    path('navbar-info', NavBarInfoView.as_view(), name='nav_bar_info'),
    path('developers', DeveloperListView.as_view(), name='developers_list'),
    path('post/bookmark/<int:post_id>', BookmarkToggleView.as_view(), name='post_bookmark'),
    path('my-bookmarks', MyBookmarksView.as_view(), name='my_bookmarks'),
    path('search', GlobalSearchView.as_view(), name='global_search'),
    path('post/public/<int:post_id>/', PublicPostDetailView.as_view(), name='post_public_detail'),
]
