from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'orders'

urlpatterns = [
    # Home page (after login)
    path('', views.home, name='home'),

    path('upload/', views.upload, name='upload'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Auth: login/logout using built-in views and templates we supply
    path('login/', auth_views.LoginView.as_view(template_name='orders/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Signup (custom)
    path('signup/', views.signup, name='signup'),
]
