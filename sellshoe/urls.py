from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'sellshoe'

urlpatterns = [
    path('sell/', views.sell_page, name='sell_page'),
    path('sell/do/', views.sell_do, name='sell_do'),                 # NEW (AJAX sell)
    path('ajax/sizes/', views.sizes_for_type, name='sizes_for_type'),
    path('ajax/colors/', views.colors_for_size, name='colors_for_size'),
    path('get_shoe_image/', views.get_shoe_image, name='get_shoe_image'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)