# shoe_stock/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'shoe_stock'


urlpatterns = [
    path('edit/<int:shoe_id>/', views.edit_shoe, name='edit_shoe'),  # URL for editing shoe
    path('delete/<int:shoe_id>/', views.delete_shoe, name='delete_shoe'),  # URL for deleting shoe
    path('', views.all_stock, name='all_stock'),  # URL for all stock page

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)