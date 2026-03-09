from django.urls import path
from . import views

urlpatterns = [
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('', views.dashboard_view, name='dashboard'),
      path("progress/", views.progress_view, name="progress"),
]