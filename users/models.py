from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        """
        Creates and returns a user with an email, full name, and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """
        Creates and returns a superuser with an email, full name, and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, full_name, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Remove the username field
    email = models.EmailField(unique=True)  # Make email unique
    full_name = models.CharField(max_length=255)  # Add full_name field

    # Set the email field as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # Make full_name a required field

    objects = CustomUserManager()

    def __str__(self):
        return self.email

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

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
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
    facebook_link = models.CharField(max_length=255, null=True, blank=True)
    instagram_link = models.CharField(max_length=255, null=True, blank=True)
    linkedin_link = models.CharField(max_length=255, null=True, blank=True)
    github_link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.user.full_name} - Profile'
