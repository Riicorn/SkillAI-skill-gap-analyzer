from django.urls import path
from .views import generate_learning_path
from . import views

urlpatterns = [
    path('learning-path/', generate_learning_path, name='learning_path'),
    path("courses/", views.courses_view, name="courses"),
    path("progress/", views.progress_view, name="progress"),
    path("toggle-save/", views.toggle_save, name="toggle_save"),
    path('toggle-complete/', views.toggle_complete, name='toggle_complete'),
    path("add-review/<int:resource_id>/", views.add_review, name="add_review"),
    path(
        "complete-resource/<int:resource_id>/",
        views.complete_resource,
        name="complete_resource"
    ),
    path('claim-badge/<int:badge_id>/', views.claim_badge, name='claim_badge'),
]