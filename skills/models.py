from django.db import models
from django.contrib.auth.models import User


# =========================================
# 1️⃣ Skill Model
# =========================================
class Skill(models.Model):

    CATEGORY_CHOICES = [
        ('Programming', 'Programming'),
        ('Data Science', 'Data Science'),
        ('Web Development', 'Web Development'),
        ('AI/ML', 'AI/ML'),
        ('Soft Skills', 'Soft Skills'),
        ('Cloud', 'Cloud'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty_level = models.IntegerField(default=1)  # 1 (Beginner) - 5 (Expert)
    is_trending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================================
# 2️⃣ Job Role Model
# =========================================
class JobRole(models.Model):

    title = models.CharField(max_length=100)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    experience_required = models.IntegerField(default=0)  # Years
    average_salary = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    skills = models.ManyToManyField(
        Skill,
        through='JobRoleSkill',
        related_name='job_roles'
    )

    def __str__(self):
        return self.title


# =========================================
# 3️⃣ Job Role Required Skills (Through Model)
# =========================================
class JobRoleSkill(models.Model):

    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    required_level = models.IntegerField(default=3)  # 1-5 scale
    priority = models.IntegerField(default=3)  # 1 (Low) - 5 (High/Core)

    class Meta:
        unique_together = ('job_role', 'skill')

    def __str__(self):
        return f"{self.job_role.title} - {self.skill.name}"


# =========================================
# 4️⃣ User Skill Model
# =========================================
class UserSkill(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    level = models.IntegerField(default=1)  # 1-5 scale
    confidence_level = models.IntegerField(default=3)  # 1-5 scale
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} - {self.skill.name}"


# =========================================
# 5️⃣ Learning Resources Model
# =========================================
class LearningResource(models.Model):

    RESOURCE_TYPE_CHOICES = [
        ('Course', 'Course'),
        ('YouTube', 'YouTube'),
        ('Article', 'Article'),
        ('Documentation', 'Documentation'),
        ('Project', 'Project'),
    ]

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='resources'
    )

    title = models.CharField(max_length=200)
    link = models.URLField()
    resource_type = models.CharField(
        max_length=50,
        choices=RESOURCE_TYPE_CHOICES
    )
    is_free = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skill.name} - {self.title}"

from django.contrib.auth.models import User

class LearningProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
    resource = models.ForeignKey('LearningResource', on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.skill.name}"