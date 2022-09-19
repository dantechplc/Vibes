from unicodedata import category

from .views import *
from django.urls import path

#app_name = 'blog'

urlpatterns = [
    path('', IndexView.as_view(), name="home"),
    path("post/<slug>", PostDetailView.as_view(), name='post_detail'),
    path('like/<int:id>', like_post, name='like_post'),
    path('fav/<int:id>', fav_post, name='fav_post'),
    path('favourite-post', favourite_list, name='fav_list'),
    path('tag/<slug:tag_slug>/', tag_list, name='post_tag'),
    path('category/<str:name>/', category_list, name='post_category'),
    path('search-post/', search_post, name='search-post'),
    path('search/', search_view, name='search'),
    path('category/', categories, name='category'),

]
