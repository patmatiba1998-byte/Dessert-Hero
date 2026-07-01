from django import forms
from django.core.validators import MinValueValidator
from shoe_input.models import Shoe

class SellForm(forms.Form):
    shoe_type = forms.ChoiceField(
        choices=Shoe.SHOE_TYPES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )
    size = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )
    color = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )
    pieces = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 101)],
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'})
    )
    price_per_piece = forms.DecimalField(
        min_value=0.01, decimal_places=2, max_digits=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ksh for one piece', 'required': 'required'})
    )

    shoe_image_url = None  # To store image URL

    def __init__(self, *args, **kwargs):
        # Allow dynamic population based on form data
        shoe_type = kwargs.get('shoe_type', None)
        size = kwargs.get('size', None)
        color = kwargs.get('color', None)
        
        super().__init__(*args, **kwargs)
        
        # Set initial choices for size and color
        self.fields['size'].choices = [('', 'Select size')]
        self.fields['color'].choices = [('', 'Select color')]

        # Retrieve size and color options based on shoe_type
        if shoe_type:
            sizes = Shoe.objects.filter(shoe_type=shoe_type).values('size').distinct()
            self.fields['size'].choices += [(size['size'], size['size']) for size in sizes]
        
        if size and shoe_type:
            colors = Shoe.objects.filter(shoe_type=shoe_type, size=size).values('color').distinct()
            self.fields['color'].choices += [(color['color'], color['color']) for color in colors]
        
        # Fetch the image URL for the selected shoe
        if shoe_type and size and color:
            try:
                shoe = Shoe.objects.get(shoe_type=shoe_type, size=size, color=color)
                self.shoe_image_url = shoe.picture.url  # Store the shoe image URL
            except Shoe.DoesNotExist:
                self.shoe_image_url = None

    def get_shoe_image_url(self, shoe_type, size, color):
        """Fetch the image URL for a given shoe type, size, and color."""
        try:
            shoe = Shoe.objects.get(shoe_type=shoe_type, size=size, color=color)
            return shoe.picture.url if shoe.picture else None
        except Shoe.DoesNotExist:
            return None
