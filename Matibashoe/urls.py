from django.contrib import admin
from django.urls import path, include
from Matibashoe import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
        path('', views.home, name='index'),
        path('users/', include('users.urls')),
        path('shoe_input/', include('shoe_input.urls')),
        path('sellshoe/', include('sellshoe.urls')),  
        path('shoe-stock/', include('shoe_stock.urls')),
        path('shoe-sells/', include('allshoesells.urls')),
        path('analytics/', include('analytics.urls')),  # Include the analytics URLs





]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

