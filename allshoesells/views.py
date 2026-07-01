# allshoesells/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from sellshoe.models import Sale
from shoe_input.models import Shoe
from django.db.models import Sum




def all_sells(request):
    # Search functionality
    search_query = request.GET.get('search', '')
    shoes = Sale.objects.all()

    if search_query:
        shoes = shoes.filter(Q(shoe_type__icontains=search_query) |
                             Q(color__icontains=search_query))

    # Sorting shoes alphabetically by type
    shoes = shoes.order_by('shoe_type')

    # Calculate total selling price
    total_selling_price = Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

    return render(request, 'all_sells.html', {
        'shoes': shoes,
        'search_query': search_query,
        'total_selling_price': total_selling_price,  # Pass the total selling price to the template
    })

def edit_shoesell(request, shoe_id):
    shoe = get_object_or_404(Sale, pk=shoe_id)
    
    if request.method == 'POST':
        shoe.shoe_type = request.POST.get('shoe_type')
        shoe.size = request.POST.get('size')
        shoe.color = request.POST.get('color')

        if request.FILES.get('picture'):
            shoe.picture = request.FILES['picture']
        
        shoe.save()
        messages.success(request, 'Shoe updated successfully!')
        return redirect('allshoesells:all_sells')  # Redirect to all stock page after update
    
    # Pass 'Shoe.SHOE_TYPES' to the template
    return render(request, 'all_sells.html', {
        'shoe': shoe, 
        'shoe_types': Sale.shoe_type,  # Add this line
    })



def delete_shoesell(request, shoe_id):
    shoe = get_object_or_404(Sale, pk=shoe_id)
    
    if request.method == 'POST':
        shoe.delete()
        messages.success(request, 'Shoe deleted successfully!')
        return redirect('allshoesells:all_sells')  # Redirect to all stock page after deletion
    
    return redirect('allshoesells:all_sells')  # If not POST, just redirect (add proper handling)