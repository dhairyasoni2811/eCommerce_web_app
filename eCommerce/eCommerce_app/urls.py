from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_item", views.new_item, name="new_item"),
    path("details/<int:item_id>", views.details, name="details"),
    path("add_comment", views.add_comment, name="add_comment"),
    path("get_comments/<int:item_id>", views.get_comments, name="get_comments"),
]