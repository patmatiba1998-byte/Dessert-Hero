from django.contrib import admin
from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sold_at', 'shoe_type', 'size', 'color', 'pieces', 'price_per_piece', 'total_price', 'shoe_image_display', 'user_added', 'date_added')
    list_filter = ('shoe_type', 'size', 'color', 'sold_at', 'user_added', 'date_added')
    search_fields = ('shoe_type', 'color', 'size', 'user_added', 'date_added')  # Added size to search fields

    # Add a method to display shoe image in the admin list view
    def shoe_image_display(self, obj):
        if obj.shoe_image:
            return f'<img src="{obj.shoe_image.url}" width="50px" />'
        return 'No Image'
    shoe_image_display.allow_tags = True  # Allow HTML tags (for displaying image)
    shoe_image_display.short_description = 'Shoe Image'  # Column name

    # Optional: You can customize the edit form (for inline updates) if needed here.
    # fieldsets = (
    #     (None, {
    #         'fields': ('shoe_type', 'size', 'color', 'pieces', 'price_per_piece', 'total_price', 'shoe_image')
    #     }),
    # ) 

