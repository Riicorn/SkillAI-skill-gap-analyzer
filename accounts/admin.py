from django.contrib import admin
from .models import UserProfile, CareerProgress, Achievement
from recommendations.models import SavedResource, UserAchievement


# =========================================
# 1️⃣ User Profile Admin
# =========================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'career_goal',
        'experience_level',
        'skill_score',
        'profile_completion',
        'is_verified',
    )

    search_fields = ('user__username', 'career_goal')
    list_filter = ('experience_level', 'is_verified')
    readonly_fields = ('created_at', 'updated_at')

    list_per_page = 10
    ordering = ('-created_at',)

   
# =========================================
# 2️⃣ Career Progress Admin
# =========================================
@admin.register(CareerProgress)
class CareerProgressAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'job_role',
        'completion_percentage',
        'last_evaluated',
    )

    search_fields = ('user__username', 'job_role')
    list_filter = ('completion_percentage',)

    list_per_page = 10
    ordering = ('-completion_percentage',)


# =========================================
# 3️⃣ Achievement Admin
# =========================================
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'title',
        'earned_at',
    )

    search_fields = ('user__username', 'title')

    list_per_page = 10
    ordering = ('-earned_at',)


@admin.register(SavedResource)
class SavedResourceAdmin(admin.ModelAdmin):
    list_display = ('user', 'resource')
    search_fields = ('user__username', 'resource__title')
    list_per_page = 10

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_claimed', 'date_earned')
    list_filter = ('is_claimed',)
    search_fields = ('user__username', 'name')
    ordering = ('-date_earned',)


    