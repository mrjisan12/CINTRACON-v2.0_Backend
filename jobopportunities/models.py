from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

class JobPost(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField() 
    company_name = models.CharField(max_length=100)
    salary = models.PositiveIntegerField() 
    place = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    apply_link = models.CharField(max_length=200)
    job_post_image = CloudinaryField('job_post_image', blank=True, null=True)
    deadline = models.DateField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posts')

    def __str__(self):
        return f"{self.title} - {self.company_name} - {self.user.full_name}"
