from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Handles the root URL: /
    path('items/', views.item_list, name='item_list'),
    path('rate/<int:item_id>/', views.rate_item, name='rate_item'),
    # Add your other URLs here
]
