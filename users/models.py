from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
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

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=50, choices=DEPARTMENTS)
    semester = models.CharField(max_length=50, choices=SEMESTERS)
    section = models.CharField(max_length=50,choices=SECTIONS,null=True)
    batch_no = models.IntegerField()
    points = models.IntegerField(default=0)
    phone_no = models.CharField(max_length=12, null=True, blank=True)
    blood_grp = models.CharField(max_length=10, null=True, blank=True)
    bio = models.CharField(max_length=150, null=True, blank=True)
    relationship_status = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_photo = CloudinaryField('profile_photo', null=True, blank=True)
    cover_photo = CloudinaryField('cover_photo', null=True, blank=True)

    def __str__(self):
        return self.user.email
