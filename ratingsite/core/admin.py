from django.contrib import admin
from .models import Item, Token, Rating

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "avg_appearance", "avg_personality", "avg_total", "ratings_count")

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("value", "active", "created_at")

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("token", "item", "appearance_score", "personality_score", "created_at")