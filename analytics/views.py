from django.shortcuts import render
from django.db.models import Sum, F
from django.db.models.functions import TruncDay, TruncWeek
from shoe_input.models import Shoe
from sellshoe.models import Sale
import json

def analytics(request):
    # Initialize the profit margin data
    profit_margin_data = []
    
    # Retrieve all shoes
    shoes = Shoe.objects.all()
    
    # Calculate profit margin data (buying price vs selling price)
    for shoe in shoes:
        sales = Sale.objects.filter(shoe_type=shoe.shoe_type, size=shoe.size, color=shoe.color)
        for sale in sales:
            # Calculate profit margin in percentage
            profit_margin = float((sale.price_per_piece - shoe.buying_price) / shoe.buying_price * 100)
            # Add the weekly profit margin (using week number YYYY-WW)
            profit_margin_data.append({'week': sale.sold_at.strftime('%Y-%U'), 'profit_margin': profit_margin})

    # Aggregate total selling price over time (daily)
    daily_sales = Sale.objects.annotate(day=TruncDay('sold_at')) \
                              .values('day') \
                              .annotate(total_sales=Sum('total_price')) \
                              .order_by('day')

    # Aggregate total pieces sold over time (daily)
    daily_pieces = Sale.objects.annotate(day=TruncDay('sold_at')) \
                               .values('day') \
                               .annotate(total_pieces=Sum('pieces')) \
                               .order_by('day')

    # Calculate shoe popularity based on total sales per shoe type
    shoe_popularity = Sale.objects.values('shoe_type') \
                                  .annotate(total_sales=Sum('pieces')) \
                                  .order_by('-total_sales')

    # Convert daily sales and pieces data into serializable format (convert Decimal to float)
    daily_sales = [{
        'day': sale['day'].strftime('%Y-%m-%d'),
        'total_sales': float(sale['total_sales'])
    } for sale in daily_sales]

    daily_pieces = [{
        'day': piece['day'].strftime('%Y-%m-%d'),
        'total_pieces': float(piece['total_pieces'])
    } for piece in daily_pieces]

    shoe_popularity = [{
        'shoe_type': shoe['shoe_type'],
        'total_sales': float(shoe['total_sales'])
    } for shoe in shoe_popularity]

    # Weekly Profit Margin Data (grouped by week)
    weekly_profit_margin = {}
    for entry in profit_margin_data:
        week = entry['week']
        profit_margin = entry['profit_margin']
        if week not in weekly_profit_margin:
            weekly_profit_margin[week] = []
        weekly_profit_margin[week].append(profit_margin)

    # Calculate average profit margin per week
    profit_margin_data_weekly = [{
        'week': week,
        'profit_margin': sum(profit_margin_list) / len(profit_margin_list)  # Average profit margin per week
    } for week, profit_margin_list in weekly_profit_margin.items()]

    # Revenue vs Cost comparison (daily aggregation)
    revenue_vs_cost = []
    sales = Sale.objects.all()
    for sale in sales:
        shoe = Shoe.objects.get(shoe_type=sale.shoe_type, size=sale.size, color=sale.color)  # Get the related shoe
        total_cost = sale.pieces * shoe.buying_price  # Calculate the cost based on pieces sold and buying price
        revenue_vs_cost.append({
            'day': sale.sold_at.strftime('%Y-%m-%d'),
            'total_sales': float(sale.total_price),
            'total_cost': float(total_cost)
        })

    # Convert all querysets to JSON data for JavaScript
    return render(request, 'analytics.html', {
        'profit_margin_data': json.dumps(profit_margin_data_weekly),  # Pass weekly profit margin data
        'daily_sales': json.dumps(daily_sales),
        'daily_pieces': json.dumps(daily_pieces),
        'shoe_popularity': json.dumps(shoe_popularity),
        'revenue_vs_cost': json.dumps(revenue_vs_cost),  # Include revenue vs cost data
    })
