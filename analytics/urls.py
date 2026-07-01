from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('analytics/', views.analytics, name='analytics_page'),  # Define URL pattern for Analytics page
]
