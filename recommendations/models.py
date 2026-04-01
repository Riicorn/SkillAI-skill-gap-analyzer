from django.db import models
from django.contrib.auth.models import User

from skills.models import LearningResource

class UserAchievement(models.Model):  # Keep this name
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_claimed = models.BooleanField(default=False)
    date_earned = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class SavedResource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} saved {self.resource.title}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)

    text = models.TextField()
    rating = models.IntegerField(default=0)  # optional ⭐

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.resource.title}"        