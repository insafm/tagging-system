from django.urls import path
from rest_framework import renderers
from .views import AddPost, Reset, Posts
from .viewset import PostViewSet, UserViewSet, ReactionViewSet

app_name = 'post'

posts_list = PostViewSet.as_view({
    'get': 'list',
})

users_list = UserViewSet.as_view({
    'post': 'create',
})

reaction_list = ReactionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = [
	path('add', AddPost.as_view(), name='add_post'),
	path('admin-list-post', Posts.as_view(), name='admin_list_post'),

    path('list', posts_list, name='posts_list'),
    path('user', users_list, name='users_list'),
    path('react', reaction_list, name='reaction_list'),
	
	path('reset-system', Reset.as_view(), name='reset_system'),
]