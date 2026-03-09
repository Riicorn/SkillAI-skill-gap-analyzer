import numpy as np
from .models import JobRoleSkill, UserSkill


def calculate_skill_gap(user, job_role):

    gaps_dict = {}
    weights = []
    scores = []

    required_skills = JobRoleSkill.objects.filter(job_role=job_role)

    if not required_skills.exists():
        return {}, 0

    for req in required_skills:

        try:
            user_skill = UserSkill.objects.get(user=user, skill=req.skill)
            user_level = user_skill.level
        except UserSkill.DoesNotExist:
            user_level = 0

        if req.required_level > 0:
            match_percentage = (user_level / req.required_level) * 100
        else:
            match_percentage = 0

        match_percentage = min(round(match_percentage), 100)

        # Store only skills that need improvement
        if match_percentage < 100:
            gaps_dict[req.skill.name] = match_percentage

        scores.append(match_percentage)
        weights.append(req.priority if req.priority else 1)

    total_gap_score = round(np.average(scores, weights=weights)) if scores else 0

    return gaps_dict, total_gap_score