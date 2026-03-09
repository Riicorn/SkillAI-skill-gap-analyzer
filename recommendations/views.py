from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from skills.models import UserSkill, JobRoleSkill
from skills.models import UserSkill, LearningResource  # Ensure LearningResource is imported
# Import from the 'skills' app where these models actually live
from skills.models import UserSkill, JobRoleSkill, LearningResource, JobRole

@login_required
def generate_learning_path(request):
    user = request.user
    
    # 1. Get the user's target job role (e.g., from their profile or a selection)
    # For this example, we'll take the first one or one you've saved in the session
    target_role = JobRole.objects.first() 
    
    # 2. Find all skills REQUIRED for this specific Job Role
    required_skills = JobRoleSkill.objects.filter(job_role=target_role).select_related('skill')
    
    # 3. Get the user's CURRENT skills
    user_skills = UserSkill.objects.filter(user=user).values_list('skill_id', 'level')
    user_skill_dict = {skill_id: level for skill_id, level in user_skills}
    
    roadmap_items = []
    
    for req in required_skills:
        current_level = user_skill_dict.get(req.skill.id, 0)
        
        # 4. If the user is below the required level for the JOB, add to roadmap
        if current_level < req.required_level:
            # Fetch the best resources for this gap
            resources = LearningResource.objects.filter(skill=req.skill)[:3]
            
            roadmap_items.append({
                'skill': req.skill,
                'target_level': req.required_level,
                'current_level': current_level,
                'resources': resources,
                'gap_severity': req.required_level - current_level
            })

    return render(request, "recommendations/learning_path.html", {
        "roadmap_items": roadmap_items,
        "target_role": target_role
    })
def courses_view(request):
    return render(request, "recommendations/courses.html")