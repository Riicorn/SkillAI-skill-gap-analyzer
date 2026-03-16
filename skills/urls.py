from django.urls import path
from . import views

urlpatterns = [
    path('my-skills/', views.skills_view, name='skills'),
    path('skill-gap/', views.skill_gap_view, name='skill_gap'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('delete-skill/<int:id>/', views.delete_skill, name="delete_skill"),
    
]