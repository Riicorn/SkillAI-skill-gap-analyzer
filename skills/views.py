from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

from .models import JobRole, Skill, UserSkill
from .utils import calculate_skill_gap

# Homepage
def home(request):
    return HttpResponse("SkillAI is Running 🚀")


# Landing page
def landing(request):
    return render(request, "landing.html")


# My Skills page


@login_required
def skills_view(request):
    # Fetch UserSkills and select the related Skill name to avoid the 'Field Error'
    user_skills = UserSkill.objects.filter(user=request.user).select_related('skill')

    if request.method == "POST":
        skill_name_str = request.POST.get('skill_name')
        level = request.POST.get('level')

        if skill_name_str and level:
            # 1. Get the master Skill object
            skill_obj = Skill.objects.get(name=skill_name_str)
            
            # 2. Update existing level or create new entry
            UserSkill.objects.update_or_create(
                user=request.user, 
                skill=skill_obj, 
                defaults={'level': int(level)}
            )
            messages.success(request, f"Your {skill_name_str} skill has evolved!")
            return redirect('skills')

    return render(request, "skills/skills.html", {"skills": user_skills})


# Skill Gap page
@login_required
def skill_gap_view(request):

    job_role = JobRole.objects.first()

    if not job_role:
        return render(request, "skills/skill_gap.html", {"no_roles": True})

    user_skills = UserSkill.objects.filter(user=request.user)

    if not user_skills.exists():
        return render(request, "skills/skill_gap.html", {
            "job_role": job_role,
            "has_skills": False
        })

    gaps, total_gap_score = calculate_skill_gap(request.user, job_role)

    # Sort weakest skills first
    gaps = dict(sorted(gaps.items(), key=lambda x: x[1]))

    context = {
        "job_role": job_role,
        "gaps": gaps,
        "total_gap_score": total_gap_score,
        "has_skills": True
    }

    return render(request, "skills/skill_gap.html", context)



def upload_resume(request):
    if request.method == "POST" and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        
        # Here you can save the file to a model or process it with AI
        # For now, let's just show a success message
        messages.success(request, f"Resume '{resume_file.name}' uploaded successfully!")
        
        return redirect('skills') # Redirect back to the skills page
    
    return redirect('skills')