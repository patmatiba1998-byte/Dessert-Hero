# users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('verify-code/', views.verify_code_view, name='verify_code'), 
    path('dashboard1/', views.dashboard1_view, name='dashboard1'), 
    path('dashboard2/', views.dashboard2_view, name='dashboard2'), 
]
