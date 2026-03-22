from django.db import models
from django.contrib.auth.models import User

class UserAchievement(models.Model):  # Keep this name
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_claimed = models.BooleanField(default=False)
    date_earned = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"