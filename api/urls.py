from django.urls import path
from api import views

urlpatterns = [
    path("login/", views.login),
    path("is_unique/", views.is_unique),
    path("signup/", views.signup),
    path("mypage/<int:user_id>/", views.mypage),
    path("mypage/get_following_or_followers/<int:user_id>/<str:following_or_follwers>/", views.get_following_or_followers),
    path("mypage_login/", views.mypage_login),
    path("mypage_login/update_user_info/", views.update_user_info),
    path("mypage_login/get_draft/", views.get_draft),
    path("mypage_login/delete_post_or_draft/", views.delete_post_or_draft),
    path("mypage_login/follow/", views.follow),
    path("mypage_login/unfollow/", views.unfollow),
    path("mypage_login/like/", views.like),
    path("mypage_login/unlike/", views.unlike),
    path("mypage_login/favorite/", views.favorite),
    path("mypage_login/unfavorite/", views.unfavorite),
    path("post_or_draft/", views.post_or_draft),
    path("contents/<int:post_id>/", views.get_contents),
    path("search_results/<str:keyword>/<str:target>/<int:page>/", views.search_results),
    path("send_email/", views.send_email),

    # DEBUG: below
    path("delete_users/", views.delete_users),
    path("debug/", views.debug),
]