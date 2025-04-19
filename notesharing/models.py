from django.db import models
from cloudinary.models import CloudinaryField

from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

class Note(models.Model):
    
    DEPARTMENTS = (
        ('cse', 'CSE'),
        ('eee', 'EEE'),
        ('pharm', 'PHARM'),
        ('civil', 'CIVIL'),
        ('eng', 'ENG'),
        ('bba', 'BBA'),
        ('llb', 'LLB'),
        ('msc', 'M.Sc'),
        ('mba', 'MBA'),
    )

    SEMESTERS = (
        ('1.1', '1.1'),
        ('1.2', '1.2'),
        ('2.1', '2.1'),
        ('2.2', '2.2'),
        ('3.1', '3.1'),
        ('3.2', '3.2'),
        ('4.1', '4.1'),
        ('4.2', '4.2'),
        ('graduate', 'GRADUATE'),
    )
    
    SECTIONS = (
        ('A','A'),
        ('B','B'),
        ('C','C'),
        ('D','D'),
        ('E','E'),
    )

    
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    note_file = CloudinaryField('note_file', resource_type='raw', blank=True, null=True)
    drive_link = models.URLField(blank=True, null=True)
    department = models.CharField(max_length=100, choices=DEPARTMENTS)
    semester = models.CharField(max_length=10, choices=SEMESTERS)
    section = models.CharField(max_length=10, choices=SECTIONS)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_sharing')

    def __str__(self):
        return f"{self.title}-{self.user.full_name}"
