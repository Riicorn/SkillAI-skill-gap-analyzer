from django.urls import path
from .views import generate_learning_path
from . import views

urlpatterns = [
    path('learning-path/', generate_learning_path, name='learning_path'),
    path("courses/", views.courses_view, name="courses"),
    path("progress/", views.progress_view, name="progress"),

    path(
        "complete-resource/<int:resource_id>/",
        views.complete_resource,
        name="complete_resource"
    ),
    path(
    "claim-achievement/<int:badge_id>/",
    views.claim_badge,
    name="claim_badge"
)
]