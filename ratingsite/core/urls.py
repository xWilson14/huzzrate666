from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),  # Homepage - uses your existing index view
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('rate/', views.rate_item, name='rate'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('reset/', views.reset_ratings, name='reset'),
]
