from django.urls import path
from .views import generate_learning_path
from . import views

urlpatterns = [
    path('learning-path/', generate_learning_path, name='learning_path'),
    path("courses/", views.courses_view, name="courses"),
]