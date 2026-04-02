from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from skills.models import Skill, UserSkill, JobRole
import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from skills.utils import calculate_skill_gap
from allauth.account.models import EmailAddress
from allauth.account.adapter import get_adapter
# 1️⃣ Landing Page
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


# 2️⃣ Signup
# def signup_view(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('onboarding')
#     else:
#         form = UserCreationForm()

#     return render(request, 'accounts/signup.html', {'form': form})
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 🔥 send email confirmation (new way)
            get_adapter(request).send_confirmation_mail(request, user)

            return redirect('account_email_verification_sent')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


# 3️⃣ Onboarding
@login_required
def onboarding_view(request):
    job_roles = JobRole.objects.all()
    available_skills = Skill.objects.all()

    if request.method == 'POST':
        selected_role_id = request.POST.get('job_role')
        selected_skills = request.POST.getlist('skills')

        if not selected_role_id:
            return render(request, 'accounts/onboarding.html', {
                'job_roles': job_roles,
                'available_skills': available_skills,
                'error': "Please select a role."
            })

        from .models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.target_role_id = selected_role_id
        profile.save()

        for skill_id in selected_skills:
            level_value = request.POST.get(f'level_{skill_id}')

            if level_value:
                skill = Skill.objects.get(pk=skill_id)

                UserSkill.objects.update_or_create(
                    user=request.user,
                    skill=skill,
                    defaults={"level": int(level_value)}
                )

        return redirect('dashboard')

    return render(request, 'accounts/onboarding.html', {
        'job_roles': job_roles,
        'available_skills': available_skills
    })
    
# 4️⃣ Dashboard
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from skills.models import UserSkill
import json

@login_required
def dashboard_view(request):
    user = request.user

    user_skills = UserSkill.objects.filter(user=user)

    # 🔥 SORT SKILLS (highest → lowest)
    skills = user_skills.order_by('-level')



    total_skills = len(skills)

    # =============================
    # 📊 AVERAGE
    # =============================
    if total_skills > 0:
        avg_level = sum([s.level for s in skills]) / total_skills
    else:
        avg_level = 0

    avg_percentage = int((avg_level / 5) * 100)

    # =============================
    # 🧠 LEVEL
    # =============================
    if avg_percentage < 30:
        level = "Beginner"
    elif avg_percentage < 60:
        level = "Explorer"
    elif avg_percentage < 80:
        level = "Pro"
    else:
        level = "Master"

    # =============================
    # ⭐ STRONGEST & WEAKEST (SAFE)
    # =============================
    # =============================
# ⭐ STRONGEST & WEAKEST (SAFE)
# =============================
        strongest = skills.first()
        weakest = user_skills.order_by('level').first()

        strongest_skill = {
            "name": strongest.skill.name if strongest else None,
            "level": strongest.level if strongest else None
        }

        weakest_skill = {
            "name": weakest.skill.name if weakest else None,
            "level": weakest.level if weakest else None
        }
    # =============================
    # 📈 CHART DATA
    # =============================
    skill_labels = [s.skill.name for s in skills]
    skill_data = [(s.level / 5) * 100 for s in skills]

    # =============================
    # 📦 CONTEXT
    # =============================
    context = {
        "skills": skills,
        "total_skills": total_skills,
        "avg_proficiency": avg_percentage,
        "level": level,

        # 🔥 NEW (for UI)
        "strongest_skill": strongest_skill,
        "weakest_skill": weakest_skill,

        # 📊 charts
        "skill_labels": json.dumps(skill_labels),
        "skill_data": json.dumps(skill_data),
    }

    return render(request, "accounts/dashboard.html", context)
# 5️⃣ Custom Login
@login_required
def onboarding_view(request):
    job_roles = JobRole.objects.all()
    available_skills = Skill.objects.all()

    if request.method == 'POST':
        selected_role_id = request.POST.get('job_role')
        selected_skills = request.POST.getlist('skills')

        if not selected_role_id:
            return render(request, 'accounts/onboarding.html', {
                'job_roles': job_roles,
                'available_skills': available_skills,
                'error': "Please select a role."
            })

        # ✅ SAVE ROLE IN DATABASE (NOT SESSION)
        from .models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.target_role_id = selected_role_id
        profile.save()

        # ✅ SAVE SKILLS
        for skill_id in selected_skills:
            level_value = request.POST.get(f'level_{skill_id}')

            if level_value:
                skill = Skill.objects.get(pk=skill_id)

                UserSkill.objects.update_or_create(
                    user=request.user,
                    skill=skill,
                    defaults={"level": int(level_value)}
                )

        return redirect('dashboard')

    return render(request, 'accounts/onboarding.html', {
        'job_roles': job_roles,
        'available_skills': available_skills
    })

from django.shortcuts import redirect
from django.contrib.auth import authenticate, login

from django.contrib.auth.forms import AuthenticationForm # Ensure this is imported

def custom_login(request):
    if request.method == "POST":
        # Pass the POST data to the form so it can generate error messages
        form = AuthenticationForm(request, data=request.POST)
        
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect("/admin/")
            return redirect("/accounts/onboarding/")
        else:
            # If login fails, render the page again with the 'form' object containing errors
            return render(request, "account/login.html", {"form": form})

    # For a GET request, provide an empty form
    form = AuthenticationForm()
    return render(request, "account/login.html", {"form": form})

    from django.contrib.auth.decorators import login_required
from skills.models import UserSkill, JobRole
from recommendations.models import UserAchievement
from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Achievement

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserProfile, Achievement, CareerProgress
from recommendations.models import UserAchievement

@login_required
def profile_view(request):

    user = request.user

    profile, created = UserProfile.objects.get_or_create(user=user)

    # ✅ ONLY CLAIMED BADGES
    claimed_achievements = UserAchievement.objects.filter(
        user=request.user,
        is_claimed=True
    )

    # ✅ Career progress
    progress = CareerProgress.objects.filter(user=user)

    if not progress.exists() and profile.career_goal:
        CareerProgress.objects.create(
        user=user,
        job_role=profile.career_goal,
        completion_percentage=10
    )
    progress = CareerProgress.objects.filter(user=user)
    total_achievements = claimed_achievements.count()

    # =============================
    # Profile completion
    # =============================

    fields = [
        profile.profile_picture,
        profile.bio,
        profile.career_goal,
        profile.current_education,
        profile.university,
        profile.linkedin,
        profile.github,
        profile.portfolio,
        profile.resume,
    ]

    filled = sum(1 for f in fields if f)
    completion = int((filled / len(fields)) * 100)

    if profile.profile_completion != completion:
        profile.profile_completion = completion
        profile.save(update_fields=["profile_completion"])

    context = {
        "profile": profile,
        "claimed_achievements": claimed_achievements,  # ✅ FIXED
        "progress": progress,
        "total_achievements": total_achievements,
        "skill_score": profile.skill_score,
        "profile_completion": profile.profile_completion,
    }

    return render(request, "accounts/profile.html", context)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserProfile


@login_required
def edit_profile(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        profile.profile_picture = request.FILES.get("profile_picture")
        profile.bio = request.POST.get("bio")
        profile.career_goal = request.POST.get("career_goal")
        profile.current_education = request.POST.get("education")
        profile.university = request.POST.get("university")

        profile.linkedin = request.POST.get("linkedin")
        profile.github = request.POST.get("github")
        profile.portfolio = request.POST.get("portfolio")

        if request.FILES.get("resume"):
            profile.resume = request.FILES.get("resume")

        profile.save()

        return redirect("profile")

    return render(request, "accounts/edit_profile.html", {"profile": profile})