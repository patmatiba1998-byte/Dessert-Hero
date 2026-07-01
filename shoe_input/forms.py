# shoe_input/forms.py
from django import forms
from .models import Shoe

class ShoeForm(forms.ModelForm):
    class Meta:
        model = Shoe
        fields = ['shoe_type', 'size', 'color', 'pieces', 'buying_price', 'picture']
        widgets = {
            'shoe_type': forms.Select(choices=Shoe.SHOE_TYPES, attrs={'class': 'form-select'}),
            'size': forms.Select(choices=[(i, i) for i in range(35, 56)], attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Black'}),
            'pieces': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'buying_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in Ksh'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }
