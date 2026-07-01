# shoe_stock/views.py
from django.shortcuts import render, get_object_or_404, redirect
from shoe_input.models import Shoe
from django.db.models import Q
from django.contrib import messages
from django.db.models import Sum



def all_stock(request):
    # Search functionality
    search_query = request.GET.get('search', '')
    shoes = Shoe.objects.all()

    if search_query:
        shoes = shoes.filter(Q(shoe_type__icontains=search_query) |
                             Q(color__icontains=search_query))

    # Sorting shoes alphabetically by type
    shoes = shoes.order_by('shoe_type')

    # Calculate total buying price from Shoe model
    total_buying_price = Shoe.objects.aggregate(Sum('buying_price'))['buying_price__sum'] or 0

    return render(request, 'all_stock.html', {
        'shoes': shoes,
        'search_query': search_query,
        'total_buying_price': total_buying_price,  # Pass the total buying price to the template
    })

def edit_shoe(request, shoe_id):
    shoe = get_object_or_404(Shoe, pk=shoe_id)
    
    if request.method == 'POST':
        shoe.shoe_type = request.POST.get('shoe_type')
        shoe.size = request.POST.get('size')
        shoe.color = request.POST.get('color')

        if request.FILES.get('picture'):
            shoe.picture = request.FILES['picture']
        
        shoe.save()
        messages.success(request, 'Shoe updated successfully!')
        return redirect('shoe_stock:all_stock')  # Redirect to all stock page after update
    
    return redirect('shoe_stock:all_stock')  # If not POST, just redirect (add proper handling for GET)


def delete_shoe(request, shoe_id):
    shoe = get_object_or_404(Shoe, pk=shoe_id)
    
    if request.method == 'POST':
        shoe.delete()
        messages.success(request, 'Shoe deleted successfully!')
        return redirect('shoe_stock:all_stock')  # Redirect to all stock page after deletion
    
    return redirect('shoe_stock:all_stock')  # If not POST, just redirect (add proper handling)