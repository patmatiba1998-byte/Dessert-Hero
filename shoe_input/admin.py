from django.contrib import admin
from .models import Shoe

@admin.register(Shoe)
class ShoeAdmin(admin.ModelAdmin):
    list_display = ("shoe_type", "size", "color", "pieces", "buying_price", "date_added", "user_added")
    list_filter = ("shoe_type", "size", "color", "date_added", "user_added")
    search_fields = ("shoe_type", "color", "user_added")
