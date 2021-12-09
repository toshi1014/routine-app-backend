from django.urls import path
from api import views

urlpatterns = [
    path("login/", views.login),
    path("is_unique/", views.is_unique),
    path("signup/", views.signup),
    path("post/", views.post),
    path("debug/", views.debug),
]