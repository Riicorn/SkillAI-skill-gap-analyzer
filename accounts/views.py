from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from skills.models import Skill, UserSkill, JobRole
import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

# 1️⃣ Landing Page
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


# 2️⃣ Signup
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('onboarding')
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
                'error': "Please select a strategic goal."
            })

        # Save role in session
        request.session["target_role_id"] = int(selected_role_id)

        # Save user skills
        for skill_id in selected_skills:
            level_value = request.POST.get(f'level_{skill_id}')

            if level_value:
                skill = Skill.objects.get(pk=skill_id)

                UserSkill.objects.update_or_create(
                    user=request.user,
                    skill=skill,
                    defaults={
                        "level": int(level_value)
                    }
                )

        return redirect('dashboard')

    return render(request, 'accounts/onboarding.html', {
        'job_roles': job_roles,
        'available_skills': available_skills
    })                
    job_roles = JobRole.objects.all()
    available_skills = Skill.objects.all()

    if request.method == 'POST':
        selected_role_id = request.POST.get('job_role')
        selected_skills = request.POST.getlist('skills')
        selected_role_id = request.POST.get('job_role')

        if not selected_role_id:
            return render(request, 'accounts/onboarding.html', {
                'job_roles': job_roles,
                'available_skills': available_skills,
                'error': "Please select a strategic goal."
            })

        # SAVE ROLE IN SESSION
        request.session["target_role_id"] = selected_role_id

        # Save user selected skills correctly
        for skill_id in selected_skills:
            level_value = request.POST.get(f'level_{skill_id}')

            if level_value:
                skill = Skill.objects.get(id=skill_id)

                UserSkill.objects.update_or_create(
                    user=request.user,
                    skill=skill,
                    defaults={
                        'level': int(level_value)  # ✅ CORRECT FIELD NAME
                    }
                )

        return redirect('dashboard')

    return render(request, 'accounts/onboarding.html', {
        'job_roles': job_roles,
        'available_skills': available_skills
    })
# 4️⃣ Dashboard
@login_required
def dashboard_view(request):
    user = request.user
    user_skills = UserSkill.objects.filter(user=user)

    total_skills = user_skills.count()

    if total_skills > 0:
        avg_level = sum([s.level for s in user_skills]) / total_skills
    else:
        avg_level = 0

    # Convert 1-5 scale into percentage
    avg_percentage = int((avg_level / 5) * 100)

    job_match_score = avg_percentage

    # Level logic
    if avg_percentage < 30:
        level = "Beginner"
    elif avg_percentage < 60:
        level = "Explorer"
    elif avg_percentage < 80:
        level = "Pro"
    else:
        level = "AI Master"

    skill_labels = [s.skill.name for s in user_skills]
    skill_data = [(s.level / 5) * 100 for s in user_skills]

    context = {
        "total_skills": total_skills,
        "avg_proficiency": avg_percentage,
        "job_match_score": job_match_score,
        "level": level,
        "skill_labels": skill_labels,
        "skill_data": skill_data,
    }

    return render(request, "dashboard/dashboard.html", context)

# 5️⃣ Custom Login


from django.shortcuts import redirect
from django.contrib.auth import authenticate, login

def custom_login(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("/admin/")

            return redirect("/accounts/onboarding/")

    return render(request, "account/login.html")

    from django.contrib.auth.decorators import login_required
from skills.models import UserSkill
from recommendations.models import UserAchievement
from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Achievement

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserProfile, Achievement, CareerProgress


@login_required
def profile_view(request):

    user = request.user

    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Achievements
    achievements = Achievement.objects.filter(user=user)

    # Career progress
    progress = CareerProgress.objects.filter(user=user)

    total_achievements = achievements.count()

    # =============================
    # Profile completion calculation
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

    # =============================
    # Context
    # =============================

    context = {
        "profile": profile,
        "achievements": achievements,
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