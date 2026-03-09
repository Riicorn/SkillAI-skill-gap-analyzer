from django.urls import path
from allauth.account.views import LoginView # Import the Allauth view directly
from . import views
from .views import custom_login
urlpatterns = [
    
    path("login/", custom_login, name="login"),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]