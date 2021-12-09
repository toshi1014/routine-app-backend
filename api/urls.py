from django.urls import path
from api import views

urlpatterns = [
    path("login/", views.login),
    path("post/", views.post),
    path("debug/", views.debug),
]