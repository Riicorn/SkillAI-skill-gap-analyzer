from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from skills.models import LearningResource, LearningProgress, UserSkill


from skills.models import (
    UserSkill,
    JobRoleSkill,
    LearningResource,
    JobRole,
    LearningProgress
)

from accounts.models import Achievement

@login_required
def generate_learning_path(request):

    user = request.user

    role_id = request.session.get("target_role_id")
    print("SESSION ROLE ID:", role_id) 
    if role_id:
        target_role = JobRole.objects.filter(id=role_id).first()
    else:
        target_role = JobRole.objects.first()

    # required skills for this role
    required_skills = JobRoleSkill.objects.filter(
        job_role=target_role
    ).select_related("skill")

    # user skills
    user_skills = UserSkill.objects.filter(user=user).values_list("skill_id", "level")
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
                "skill": req.skill,
                "target_level": req.required_level,
                "current_level": current_level,
                "gap_severity": req.required_level - current_level,
                "resources": resources
            })

    roadmap_items = sorted(
        roadmap_items,
        key=lambda x: (x["gap_severity"], x["skill"].name),
        reverse=True
    )

    completed_steps = len(completed_resources)
    total_steps = sum(len(item["resources"]) for item in roadmap_items)

    return render(
        request,
        "recommendations/learning_path.html",
        {
            "roadmap_items": roadmap_items,
            "target_role": target_role,
            "completed_resource_ids": completed_resources,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
        },
    )

@login_required
def complete_resource(request, resource_id):

    if request.method == "POST":

        resource = get_object_or_404(LearningResource, id=resource_id)

        progress, created = LearningProgress.objects.get_or_create(
            user=request.user,
            resource=resource,
            skill=resource.skill
        )

        if not progress.completed:

            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()

            user_skill, created = UserSkill.objects.get_or_create(
                user=request.user,
                skill=resource.skill
            )

            if user_skill.level < 5:
                user_skill.level += 1
                user_skill.save()

            completed_count = LearningProgress.objects.filter(
                user=request.user,
                completed=True
            ).count()

            total_resources = LearningResource.objects.count()

            if completed_count == 1:
                Achievement.objects.get_or_create(
                    user=request.user,
                    title="First Step 🚀",
                    description="Completed your first learning resource",
                    badge_icon="⭐"
                )

            if completed_count == 5:
                Achievement.objects.get_or_create(
                    user=request.user,
                    title="Learning Streak 🔥",
                    description="Completed 5 learning resources",
                    badge_icon="🔥"
                )

            if completed_count == 10:
                Achievement.objects.get_or_create(
                    user=request.user,
                    title="Skill Builder 🧠",
                    description="Completed 10 learning resources",
                    badge_icon="🧠"
                )

            if completed_count == total_resources:
                Achievement.objects.get_or_create(
                    user=request.user,
                    title="Roadmap Master 🏆",
                    description="Completed the entire learning roadmap",
                    badge_icon="🏆"
                )

    return redirect("learning_path")

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

    # Check if roadmap completed
    total_resources = LearningResource.objects.count()

    completed_count = LearningProgress.objects.filter(
        user=request.user,
        completed=True
    ).count()

    if completed_count >= total_resources:
        Achievement.objects.get_or_create(
            user=request.user,
            name="Roadmap Master",
            description="Completed the entire learning path"
        )

    context = {
        "completed_resources": completed_resources,
        "user_skills": user_skills,
        "achievements": achievements
    }

    return render(request, "recommendations/progress.html", context)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import UserAchievement


@login_required
@require_POST
def claim_badge(request, badge_id):

    try:
        badge = UserAchievement.objects.get(
            id=badge_id,
            user=request.user
        )

        # If already claimed
        if badge.is_claimed:
            return JsonResponse({
                "status": "already_claimed",
                "claimed": True
            })

        # Claim badge
        badge.is_claimed = True
        badge.save()

        return JsonResponse({
            "status": "success",
            "claimed": True
        })

    except UserAchievement.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Badge not found"
        }, status=404)