from django.urls import path
from .views import me

urlpatterns = [
    path("me/", me, name="users-me"),
]
