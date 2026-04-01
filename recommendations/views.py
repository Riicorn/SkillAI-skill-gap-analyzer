from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from skills.models import LearningResource, LearningProgress, UserSkill
from .models import UserAchievement
from django.views.decorators.http import require_POST
from .services import toggle_save_resource, toggle_complete_resource
from .models import SavedResource

from skills.models import (
    UserSkill,
    JobRoleSkill,
    LearningResource,
    JobRole,
    LearningProgress
)
from notifications.services import create_notification
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

            # ✅ mark complete
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()

            # ✅ update skill
            user_skill, created = UserSkill.objects.get_or_create(
                user=request.user,
                skill=resource.skill
            )

            if user_skill.level < 5:
                user_skill.level += 1
                user_skill.save()

                # 🔔 Skill notification
                create_notification(
                    user=request.user,
                    title="Skill Improved",
                    message=f"{resource.skill.name} level increased",
                    type="progress"
                )

            # ✅ counts
            completed_count = LearningProgress.objects.filter(
                user=request.user,
                completed=True
            ).count()

            total_resources = LearningResource.objects.count()

            # =========================
            # 🏆 BADGES + NOTIFICATIONS
            # =========================

            # First badge
            if completed_count == 1:
                achievement, created = UserAchievement.objects.get_or_create(
                    user=request.user,
                    name="First Step",
                    description="Completed your first learning resource"
                )
                if created:
                    create_notification(
                        user=request.user,
                        title="New Badge Earned",
                        message="You unlocked 'First Step'",
                        type="badge"
                    )

            # 5 resources
            if completed_count == 5:
                achievement, created = UserAchievement.objects.get_or_create(
                    user=request.user,
                    name="Learning Streak",
                    description="Completed 5 learning resources"
                )
                if created:
                    create_notification(
                        user=request.user,
                        title="New Badge Earned",
                        message="You unlocked 'Learning Streak'",
                        type="badge"
                    )

            # 10 resources
            if completed_count == 10:
                achievement, created = UserAchievement.objects.get_or_create(
                    user=request.user,
                    name="Skill Builder",
                    description="Completed 10 learning resources"
                )
                if created:
                    create_notification(
                        user=request.user,
                        title="New Badge Earned",
                        message="You unlocked 'Skill Builder'",
                        type="badge"
                    )

            # Full roadmap badge
            if completed_count == total_resources:
                achievement, created = UserAchievement.objects.get_or_create(
                    user=request.user,
                    name="Roadmap Master",
                    description="Completed entire roadmap"
                )
                if created:
                    create_notification(
                        user=request.user,
                        title="New Badge Earned",
                        message="You unlocked 'Roadmap Master'",
                        type="badge"
                    )

                # 💼 JOB READY NOTIFICATION (ADD THIS)
                create_notification(
                    user=request.user,
                    title="Job Ready",
                    message="You are now ready for your target job role",
                    type="career"
                )

    return redirect("learning_path")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from skills.models import LearningResource, LearningProgress

@login_required
def courses_view(request):
    resources = LearningResource.objects.all().order_by('skill__name')

    progress_qs = LearningProgress.objects.filter(user=request.user)

    progress_map = {p.resource.id: p for p in progress_qs}

    total = resources.count()
    completed = progress_qs.filter(completed=True).count()

    progress_percent = int((completed / total) * 100) if total > 0 else 0
    saved_resources = set(
        SavedResource.objects.filter(user=request.user)
        .values_list("resource_id", flat=True)
    )

    return render(request, "recommendations/courses.html", {
        "resources": resources,
        "progress_map": progress_map,
        "progress_percent": progress_percent,
        "saved_resources": saved_resources   # ✅ IMPORTANT
    })



# recommendations/views.py

# recommendations/views.py




@login_required
@require_POST
def toggle_save(request):
    rid = request.POST.get("id")
    resource = get_object_or_404(LearningResource, id=rid)

    obj, created = SavedResource.objects.get_or_create(
        user=request.user,
        resource=resource
    )

    if not created:
        obj.delete()
        return JsonResponse({"saved": False})

    return JsonResponse({"saved": True})


@login_required
@require_POST
def toggle_complete(request):
    rid = request.POST.get("id")
    resource = get_object_or_404(LearningResource, id=rid)

    completed = toggle_complete_resource(request.user, resource)

    return JsonResponse({"completed": completed})
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

    achievements = UserAchievement.objects.filter(user=request.user)

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
from django.contrib.auth.decorators import login_required
from .models import UserAchievement

@login_required
def claim_badge(request, badge_id):

    if request.method == "POST":

        badge = UserAchievement.objects.filter(
            id=badge_id,
            user=request.user
        ).first()

        if not badge:
            return JsonResponse({"status": "error"})

        if badge.is_claimed:
            return JsonResponse({"status": "already_claimed"})

        badge.is_claimed = True
        badge.save()

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "invalid"})
from .models import Review

@login_required
def add_review(request, resource_id):
    if request.method == "POST":
        resource = get_object_or_404(LearningResource, id=resource_id)

        text = request.POST.get("text")
        rating = request.POST.get("rating")

        Review.objects.create(
            user=request.user,
            resource=resource,
            text=text,
            rating=rating
        )

    return redirect("courses")
