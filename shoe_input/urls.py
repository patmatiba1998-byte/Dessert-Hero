#shoe_input urls
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from . import views

app_name = 'shoe_input'

urlpatterns = [
    path('dashboard1/', views.dashboard, name='dashboard1'),
    path('addshoe/', views.add_shoe, name='add_shoe'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
