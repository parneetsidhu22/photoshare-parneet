
from django.urls import path
from . import views


urlpatterns = [
    path('',views.homepage,name="homepage"),
    path('add-friend/',views.add_friend,name="add-friend"),
    path('friend_requests/',views.friend_request_list,name="friend_request_list"),
    path('post_data/',views.post_data,name="post-data"),
    path('like_post/',views.like_post,name="like-post"),  
]
