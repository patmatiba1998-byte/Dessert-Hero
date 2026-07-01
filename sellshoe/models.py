# sellshoe/models.py
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from shoe_input.models import Shoe
from django.contrib.auth.models import User


class Sale(models.Model):
    shoe_type = models.CharField(max_length=50, choices=Shoe.SHOE_TYPES)
    size = models.IntegerField()
    color = models.CharField(max_length=50)
    pieces = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_per_piece = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    sold_at = models.DateTimeField(auto_now_add=True)
    date_added = models.DateTimeField(auto_now_add=True)
    shoe_image = models.ImageField(upload_to='sales/', null=True, blank=True)  # Store the shoe image in Sale
    user_added = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Assuming user ID 1 exists

    
    def save(self, *args, **kwargs):
        self.total_price = Decimal(self.price_per_piece) * Decimal(self.pieces)
        
        # Optionally, set the shoe image from the Shoe model when saving the sale
        if not self.shoe_image:
            try:
                # Fetch the corresponding shoe from the Shoe model
                shoe = Shoe.objects.get(shoe_type=self.shoe_type, size=self.size, color=self.color)
                self.shoe_image = shoe.picture  # Copy the shoe's image to the sale
            except Shoe.DoesNotExist:
                pass  # If the shoe doesn't exist, no image will be copied

        super().save(*args, **kwargs) 
