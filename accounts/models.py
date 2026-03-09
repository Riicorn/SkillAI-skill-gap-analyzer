from django.db import models
from django.contrib.auth.models import User


# =========================================
# 1️⃣ User Profile (Core Professional Model)
# =========================================
class UserProfile(models.Model):

    EXPERIENCE_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )

    bio = models.TextField(blank=True)

    career_goal = models.CharField(
        max_length=200,
        blank=True,
        help_text="Target role (e.g., AI Engineer)"
    )

    experience_level = models.CharField(
        max_length=50,
        choices=EXPERIENCE_CHOICES,
        default='Beginner'
    )

    current_education = models.CharField(max_length=200, blank=True)
    university = models.CharField(max_length=200, blank=True)

    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)

    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True
    )

    skill_score = models.FloatField(default=0.0)  # Calculated overall score
    profile_completion = models.IntegerField(default=0)  # 0–100%

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# =========================================
# 2️⃣ Career Progress Tracking
# =========================================
class CareerProgress(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    job_role = models.CharField(max_length=150)

    completion_percentage = models.IntegerField(default=0)

    last_evaluated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_role}"


# =========================================
# 3️⃣ Achievement System (Gamification)
# =========================================
class Achievement(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="achievements"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    badge_icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Icon name or badge reference"
    )

    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
