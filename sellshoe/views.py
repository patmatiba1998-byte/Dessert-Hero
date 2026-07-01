from decimal import Decimal
import json

from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from shoe_input.models import Shoe
from .models import Sale
from .forms import SellForm


# ---------- Helpers: compute "virtual" remaining (inventory - sold) ----------

def _all_type_values():
    # Stored values in Shoe.SHOE_TYPES (first item of each tuple)
    return [v for (v, _) in Shoe.SHOE_TYPES]

def _inventory_by_type():
    """{shoe_type: total pieces in Shoe}"""
    base = {t: 0 for t in _all_type_values()}
    for row in Shoe.objects.values('shoe_type').annotate(total=Sum('pieces')):
        base[row['shoe_type']] = row['total'] or 0
    return base

def _sold_by_type():
    """{shoe_type: total pieces already sold (Sale)}"""
    sold = {t: 0 for t in _all_type_values()}
    for row in Sale.objects.values('shoe_type').annotate(total=Sum('pieces')):
        sold[row['shoe_type']] = row['total'] or 0
    return sold

def _virtual_counts_by_type():
    """{shoe_type: inventory - sold}, never negative."""
    inv = _inventory_by_type()
    sold = _sold_by_type()
    return {t: max(0, (inv.get(t, 0) - sold.get(t, 0))) for t in inv.keys()}

def _virtual_available_for(shoe_type, size, color):
    """Remaining pieces for a specific (type, size, color) = inventory - sold."""
    inv = (
        Shoe.objects.filter(shoe_type=shoe_type, size=size, color=color)
        .aggregate(total=Sum('pieces'))['total'] or 0
    )
    sold = (
        Sale.objects.filter(shoe_type=shoe_type, size=size, color=color)
        .aggregate(total=Sum('pieces'))['total'] or 0
    )
    return max(0, inv - sold)

def _selling_total():
    return Sale.objects.aggregate(total=Sum('total_price'))['total'] or Decimal('0')

def _cards_context():
    return {
        'shoe_types': _virtual_counts_by_type(),   # virtual remaining, NOT mutating Shoe
        'selling_total': _selling_total(),         # total revenue from Sale
    }


# ---------- Pages ----------

@require_http_methods(["GET"])
def sell_page(request):
    """Render the sell page (cards + form) and fetch shoe image based on type, size, and color."""
    form = SellForm()

    shoe_image_url = None
    shoe_type = request.GET.get('shoe_type')
    size = request.GET.get('size')
    color = request.GET.get('color')

    # Fetch the image URL based on shoe_type, size, and color using the form method
    if shoe_type and size and color:
        shoe_image_url = form.get_shoe_image_url(shoe_type, size, color)  # Fetch image URL based on selection

    return render(request, 'sell_shoe.html', {
        'form': form,
        'shoe_image_url': shoe_image_url,  # Pass the image URL (or None) to the template
        **_cards_context()  # Adding the rest of the context for shoe types and selling total
    })


# ---------- Dependent dropdowns use VIRTUAL availability (>0) ----------

@require_http_methods(["GET"])
def sizes_for_type(request):
    """Distinct sizes for shoe_type with virtual availability > 0."""
    shoe_type = request.GET.get('shoe_type')
    sizes_map = {
        row['size']: row['total'] or 0
        for row in (Shoe.objects.filter(shoe_type=shoe_type)
                    .values('size').annotate(total=Sum('pieces')))
    }
    sold_map = {
        row['size']: row['total'] or 0
        for row in (Sale.objects.filter(shoe_type=shoe_type)
                    .values('size').annotate(total=Sum('pieces')))
    }
    sizes = [sz for sz, total in sizes_map.items() if max(0, total - sold_map.get(sz, 0)) > 0]
    sizes.sort()
    return JsonResponse({'sizes': sizes})

@require_http_methods(["GET"])
def colors_for_size(request):
    """Distinct colors for (shoe_type, size) with virtual availability > 0."""
    shoe_type = request.GET.get('shoe_type')
    size = request.GET.get('size')

    colors_map = {
        row['color']: row['total'] or 0
        for row in (Shoe.objects.filter(shoe_type=shoe_type, size=size)
                    .values('color').annotate(total=Sum('pieces')))
    }
    sold_map = {
        row['color']: row['total'] or 0
        for row in (Sale.objects.filter(shoe_type=shoe_type, size=size)
                    .values('color').annotate(total=Sum('pieces')))
    }
    colors = [c for c, total in colors_map.items() if max(0, total - sold_map.get(c, 0)) > 0]
    colors.sort()
    return JsonResponse({'colors': colors})


# ---------- SELL via JSON (fetch) — only INSERT into Sale ----------

@require_http_methods(["POST"])
def sell_do(request):
    """
    Body JSON: {shoe_type, size, color, pieces, price_per_piece}
    Returns:   {ok, message, shoe_types, selling_total}
    This DOES NOT modify shoe_input.Shoe. It only records Sale,
    and shows "virtual" remaining (inventory - sold) on this page.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    # Basic validation
    required = ['shoe_type', 'size', 'color', 'pieces', 'price_per_piece']
    missing = [k for k in required if payload.get(k) in (None, '', [])]
    if missing:
        return JsonResponse({'ok': False, 'error': f"Missing fields: {', '.join(missing)}"}, status=400)

    shoe_type = payload['shoe_type']
    color = payload['color']
    try:
        size = int(payload['size'])
        pieces = int(payload['pieces'])
        price_per_piece = Decimal(str(payload['price_per_piece']))
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid number format for size/pieces/price.'}, status=400)

    if pieces < 1 or pieces > 20 or price_per_piece <= 0:
        return JsonResponse({'ok': False, 'error': 'Pieces must be 1–20 and price > 0.'}, status=400)

    # Check VIRTUAL availability (inventory - already sold). Do NOT mutate Shoe.
    # We still use a transaction and lock the corresponding Shoe rows to reduce race conditions.
    with transaction.atomic():
        # Lock any matching Shoe rows so two sells don't read the same availability concurrently.
        _ = list(Shoe.objects.select_for_update().filter(shoe_type=shoe_type, size=size, color=color))
        available = _virtual_available_for(shoe_type, size, color)
        if pieces > available:
            return JsonResponse({'ok': False, 'error': f"Not enough stock. Available: {available}"}, status=400)

        # Record the sale ONLY.
        Sale.objects.create(
            shoe_type=shoe_type,
            size=size,
            color=color,
            pieces=pieces,
            price_per_piece=price_per_piece,
            user_added=request.user  # Add the logged-in user to the sale record
        )

    # Fresh cards (virtual) + selling total
    counts = _virtual_counts_by_type()
    selling_total = _selling_total()

    return JsonResponse({
        'ok': True,
        'message': f"Sold {pieces} pair(s) of {shoe_type} {size} {color}.",
        'shoe_types': counts,
        'selling_total': str(selling_total)
    })

@require_http_methods(["GET"])
def get_shoe_image(request):
    shoe_type = request.GET.get('shoe_type')
    size = request.GET.get('size')
    color = request.GET.get('color')

    # Ensure all parameters are provided
    if not shoe_type or not size or not color:
        return JsonResponse({'image_url': None})

    try:
        shoe = Shoe.objects.get(shoe_type=shoe_type, size=size, color=color)
        image_url = shoe.picture.url if shoe.picture else None
        return JsonResponse({'image_url': image_url})
    except Shoe.DoesNotExist:
        return JsonResponse({'image_url': None})
