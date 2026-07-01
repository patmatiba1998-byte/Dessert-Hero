# shoe_stock/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'allshoesells'

urlpatterns = [
    path('edit/<int:shoe_id>/', views.edit_shoesell, name='edit_shoesell'),  # URL for editing shoe
    path('delete/<int:shoe_id>/', views.delete_shoesell, name='delete_shoesell'),  # URL for deleting shoe
    path('', views.all_sells, name='all_sells'),  # URL for all stock page

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)