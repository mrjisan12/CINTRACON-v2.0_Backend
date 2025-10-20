from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title