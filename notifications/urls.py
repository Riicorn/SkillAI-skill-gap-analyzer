# notifications/urls.py

from django.urls import path
from . import views

urlpatterns = [
   path('', views.get_notifications, name='notifications'),
   path('all/', views.notifications_page, name='notifications_page'),
]