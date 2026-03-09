from django.contrib import admin
from .models import Skill, JobRole, JobRoleSkill, UserSkill, LearningResource


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty_level', 'is_trending')
    search_fields = ('name',)
    list_filter = ('category', 'is_trending')


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'industry', 'experience_required')
    search_fields = ('title', 'industry')


@admin.register(JobRoleSkill)
class JobRoleSkillAdmin(admin.ModelAdmin):
    list_display = ('job_role', 'skill', 'required_level', 'priority')
    list_filter = ('job_role',)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'level', 'confidence_level')


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('skill', 'title', 'resource_type', 'is_free')
    list_filter = ('resource_type', 'is_free')
    