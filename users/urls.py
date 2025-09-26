from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("health/", views.health, name="health"),
    path("me/", views.me, name="me"),
    path("auth/google/", views.google_oauth, name="google_oauth"),
    path("auth/google/test/", views.google_oauth_test, name="google_oauth_test"),
    path("profile/", views.user_profile, name="user_profile"),
]
