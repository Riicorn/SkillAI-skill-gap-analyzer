from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from skills.models import Skill, UserSkill


@login_required
def dashboard_view(request):                                
    # 1. Get User's Current Skills
    user_skills = UserSkill.objects.filter(user=request.user)
    
    skill_labels = [s.skill.name for s in user_skills]
    # Convert level (1-5) to percentage (e.g., 3 * 20 = 60%)
    skill_data = [s.level * 20 for s in user_skills]

    # 2. Get User's Target Role (Check if they have one set)
    # This assumes your User model or Profile has 'target_job'
    target_job = getattr(request.user, 'target_job', None) 
    
    missing_skills = []
    recommendations = []
    job_match_score = 0

    if target_job:
        # Get names of skills the user ALREADY has
        owned_skill_names = set(skill_labels)
        # Get names of skills REQUIRED for the target job
        required_skill_names = set(target_job.required_skills.values_list('name', flat=True))
        
        # Calculate Missing Skills
        missing_skills = list(required_skill_names - owned_skill_names)
        
        # Calculate Match Score: (Owned Skills / Required Skills) * 100
        if required_skill_names:
            match_count = len(owned_skill_names.intersection(required_skill_names))
            job_match_score = (match_count / len(required_skill_names)) * 100
            
        # Mocking some course recommendations based on missing skills
        for skill in missing_skills[:3]:  # Top 3 missing
            recommendations.append(f"Mastering {skill} for {target_job.name}")

    # 3. Metrics
    avg_proficiency = sum(skill_data) / len(skill_data) if skill_data else 0

    context = {
        "skills": user_skills,
        "skill_labels": skill_labels,
        "skill_data": skill_data,
        "total_skills": user_skills.count(),
        "avg_proficiency": round(avg_proficiency, 2),
        "job_match_score": round(job_match_score),
        
        # AI Insight Data
        "target_role_name": target_job.name if target_job else "Not Selected",
        "missing_skills": missing_skills,
        "recommendations": recommendations,
    }

    return render(request, "dashboard/dashboard.html", context)



@login_required
def onboarding_view(request):

    # Check if user already has skills
    if UserSkill.objects.filter(user=request.user).exists():
        return redirect("dashboard")

    skills = Skill.objects.all()

    if request.method == "POST":
        selected_skills = request.POST.getlist("skills")

        for skill_id in selected_skills:
            UserSkill.objects.create(
                user=request.user,
                skill_id=skill_id,
                level=1
            )

        return redirect("dashboard")

    return render(request, "accounts/onboarding.html", {"skills": skills})



# @login_required
# def progress_view(request):
#     return render(request, "dashboard/progress.html")