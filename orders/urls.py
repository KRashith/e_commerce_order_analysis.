from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
