from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

class Event(models.Model):
    EVENT_TYPES = [
        ('Conference', 'Conference'),
        ('Workshop', 'Workshop'),
        ('Contest', 'Contest'),
        ('Cultural', 'Cultural'),
        ('Seminar', 'Seminar'),
        ('Meetup', 'Meetup'),
        ('Bootcamp', 'Bootcamp'),
        ('Other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_image = CloudinaryField('event_image', blank=True, null=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    event_organizer = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='Other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return f"{self.title} - {self.event_organizer}"

    @property
    def total_interested(self):
        return self.interested_users.count()


class EventInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_interests')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='interested_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'event']  # Prevent duplicate interests

    def __str__(self):
        return f"{self.user.full_name} interested in {self.event.title}"