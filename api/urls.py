from django.urls import path
from api import views

urlpatterns = [
    path("login/", views.login),
    path("is_unique/", views.is_unique),
    path("signup/", views.signup),
    path("mypage_login/", views.mypage_login),
    path("mypage_login/update_user_info/", views.update_user_info),
    path("post_or_draft/", views.post_or_draft),
    path("debug/", views.debug),
    path("post_debug/", views.post_debug),
]