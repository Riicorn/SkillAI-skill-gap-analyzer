from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import Achievement
from skills.models import LearningProgress
from skills.models import (
    UserSkill,
    JobRoleSkill,
    LearningResource,
    JobRole,
    LearningProgress
)
@login_required
def generate_learning_path(request):

    user = request.user
    target_role = JobRole.objects.first()

    required_skills = JobRoleSkill.objects.filter(
        job_role=target_role
    ).select_related('skill')

    user_skills = UserSkill.objects.filter(user=user).values_list('skill_id', 'level')
    user_skill_dict = {skill_id: level for skill_id, level in user_skills}

    # completed resources
    completed_resources = LearningProgress.objects.filter(
        user=user,
        completed=True
    ).values_list("resource_id", flat=True)

    roadmap_items = []

    for req in required_skills:

        current_level = user_skill_dict.get(req.skill.id, 0)

        if current_level < req.required_level:

            resources = LearningResource.objects.filter(
                skill=req.skill
            ).exclude(
                id__in=completed_resources
            )[:3]

            roadmap_items.append({
                'skill': req.skill,
                'target_level': req.required_level,
                'current_level': current_level,
                'resources': resources,
                'gap_severity': req.required_level - current_level
            })

    roadmap_items = sorted(
        roadmap_items,
        key=lambda x: (x['gap_severity'], x['skill'].name),
        reverse=True
    )

    completed_steps = len(completed_resources)
    total_steps = LearningResource.objects.count()

    return render(request, "recommendations/learning_path.html", {
        "roadmap_items": roadmap_items,
        "target_role": target_role,
        "completed_resource_ids": completed_resources,
        "completed_steps": completed_steps,
        "total_steps": total_steps
    })

@login_required
def courses_view(request):

    resources = LearningResource.objects.all()

    return render(request, "recommendations/courses.html", {
        "resources": resources
    })

from skills.models import LearningProgress, UserSkill
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def progress_view(request):

    completed_resources = LearningProgress.objects.filter(
        user=request.user,
        completed=True
    ).select_related("skill", "resource")

    user_skills = UserSkill.objects.filter(
        user=request.user
    ).select_related("skill")

    achievements = Achievement.objects.filter(user=request.user)

    context = {
        "completed_resources": completed_resources,
        "user_skills": user_skills,
        "achievements": achievements
    }

    return render(request, "recommendations/progress.html", context)
@login_required
def complete_resource(request, resource_id):

    resource = LearningResource.objects.get(id=resource_id)

    progress, created = LearningProgress.objects.get_or_create(
        user=request.user,
        resource=resource,
        skill=resource.skill
    )

    if not progress.completed:

        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

        # increase skill level
        user_skill, created = UserSkill.objects.get_or_create(
            user=request.user,
            skill=resource.skill
        )

        if user_skill.level < 5:
            user_skill.level += 1
            user_skill.save()

        # COUNT completed resources
        completed_count = LearningProgress.objects.filter(
            user=request.user,
            completed=True
        ).count()

        # Achievement: first resource
        if completed_count == 1:
            Achievement.objects.get_or_create(
                user=request.user,
                title="First Step 🚀",
                description="Completed your first learning resource",
                badge_icon="⭐"
            )

        # Achievement: 5 resources
        if completed_count == 5:
            Achievement.objects.get_or_create(
                user=request.user,
                title="Learning Streak 🔥",
                description="Completed 5 learning resources",
                badge_icon="🔥"
            )

        # Achievement: 10 resources
        if completed_count == 10:
            Achievement.objects.get_or_create(
                user=request.user,
                title="Skill Builder 🧠",
                description="Completed 10 learning resources",
                badge_icon="🧠"
            )

    return redirect("learning_path")