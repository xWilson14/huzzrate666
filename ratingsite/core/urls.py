from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("rate/", views.rate_item, name="rate"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("reset/", views.reset_ratings, name="reset"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)