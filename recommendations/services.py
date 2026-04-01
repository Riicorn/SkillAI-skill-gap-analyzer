from django.utils import timezone
from skills.models import LearningProgress, UserSkill, LearningResource
from notifications.services import create_notification
from .models import UserAchievement


# =========================
# 💾 SAVE / UNSAVE
# =========================
def toggle_save_resource(user, resource: LearningResource):
    progress, _ = LearningProgress.objects.get_or_create(
        user=user,
        resource=resource,
        defaults={'skill': resource.skill}
    )

    progress.saved = not progress.saved
    progress.save()

    return progress.saved


# =========================
# ✅ COMPLETE / UNCOMPLETE (ONLY FOR COURSES PAGE)
# =========================
def toggle_complete_resource(user, resource: LearningResource):
    progress, _ = LearningProgress.objects.get_or_create(
        user=user,
        resource=resource,
        defaults={'skill': resource.skill}
    )

    progress.completed = not progress.completed

    if progress.completed:
        progress.completed_at = timezone.now()

        # 🔥 Only basic logic here (since full logic is in complete_resource)
        _handle_basic_completion(user, resource)

    else:
        progress.completed_at = None

    progress.save()

    return progress.completed


# =========================
# 🔥 BASIC LOGIC (SAFE)
# =========================
def _handle_basic_completion(user, resource):
    """
    This is a lighter version so it doesn't conflict
    with complete_resource() full logic.
    """

    user_skill, _ = UserSkill.objects.get_or_create(
        user=user,
        skill=resource.skill
    )

    if user_skill.level < 5:
        user_skill.level += 1
        user_skill.save()

        create_notification(
            user=user,
            title="Skill Improved",
            message=f"{resource.skill.name} level increased",
            type="progress"
        )

    # ✅ Badge logic (same as your existing system)
    completed_count = LearningProgress.objects.filter(
        user=user,
        completed=True
    ).count()

    if completed_count == 1:
        UserAchievement.objects.get_or_create(
            user=user,
            name="First Step",
            description="Completed your first learning resource"
        )

    elif completed_count == 5:
        UserAchievement.objects.get_or_create(
            user=user,
            name="Learning Streak",
            description="Completed 5 learning resources"
        )

    elif completed_count == 10:
        UserAchievement.objects.get_or_create(
            user=user,
            name="Skill Builder",
            description="Completed 10 learning resources"
        )