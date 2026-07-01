from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect

from .forms import ShoeForm
from .models import Shoe

def dashboard(request):
      # Fetch all shoes, sorted by shoe_type in ascending order
    shoes = Shoe.objects.all()
    # Create a dictionary with shoe types dynamically from the database if not already set
    shoe_types = {}
    for shoe in shoes:
        shoe_types[shoe.shoe_type] = shoe_types.get(shoe.shoe_type, 0) + shoe.pieces

    # (Keeping your original calc as requested)
    total_price = sum(shoe.buying_price for shoe in shoes)

    return render(request, 'dashboard1.html', {
        'shoe_types': shoe_types,
        'total_price': total_price
    })


def add_shoe(request):
    if request.method == 'POST':
        form = ShoeForm(request.POST, request.FILES)  # Make sure to include `request.FILES` here
        if form.is_valid():
            cd = form.cleaned_data
            shoe_type = cd['shoe_type']
            size = cd['size']
            color = cd['color']
            add_qty = cd['pieces']
            add_price = cd['buying_price']
            picture = cd['picture']  # Get the picture

            with transaction.atomic():
                obj, created = (
                    Shoe.objects
                    .select_for_update()
                    .get_or_create(
                        shoe_type=shoe_type,
                        size=size,
                        color=color, 
                        defaults={'pieces': add_qty, 'buying_price': add_price, 'picture': picture,  'user_added': request.user}
                    )
                )
                if not created:
                    old_qty = obj.pieces
                    new_qty = old_qty + add_qty
                    old_total = obj.buying_price * Decimal(old_qty)
                    add_total = add_price * Decimal(add_qty)
                    new_price = (old_total + add_total) / Decimal(new_qty)
                    obj.pieces = new_qty
                    obj.buying_price = new_price
                    obj.save(update_fields=['pieces', 'buying_price'])

            messages.success(request, f"Added {add_qty} piece(s) of {shoe_type} size {size} ({color}).")

            return redirect('shoe_input:add_shoe')
    else:
        form = ShoeForm()


    return render(request, 'add_shoe.html', {'form': form})

