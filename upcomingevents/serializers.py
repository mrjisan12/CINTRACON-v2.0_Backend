from rest_framework import serializers
from .models import Event, EventInterest
from cloudinary.uploader import upload
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

# User serializer
class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    profile_photo = serializers.CharField(source='profile.profile_photo.url', allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'profile_photo']


class EventSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    event_image = serializers.SerializerMethodField()
    total_interested = serializers.IntegerField(read_only=True)
    is_interested = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_image', 'date', 'location',
            'event_organizer', 'event_type', 'total_interested', 'is_interested',
            'user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_event_image(self, obj):
        if obj.event_image:
            # Remove 'image/upload/' prefix if it exists
            url = str(obj.event_image)
            if 'image/upload/' in url:
                url = url.replace('image/upload/', '')
            return url
        return None

    def get_is_interested(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return EventInterest.objects.filter(
                user=request.user, 
                event=obj
            ).exists()
        return False

    def create(self, validated_data):
        user = self.context['request'].user
        event_image = self.context['request'].FILES.get('event_image')
        event_image_url = None

        if event_image:
            try:
                # Upload to specific folder in Cloudinary
                cloudinary_response = upload(
                    event_image, 
                    folder="events"
                )
                event_image_url = cloudinary_response.get('secure_url')
            except Exception as e:
                print(f"Error uploading event image: {str(e)}")

        event = Event.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            event_image=event_image_url,
            date=validated_data['date'],
            location=validated_data['location'],
            event_organizer=validated_data['event_organizer'],
            event_type=validated_data['event_type'],
            user=user
        )
        return event


class EventInterestSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = EventInterest
        fields = ['id', 'user', 'event', 'event_title', 'created_at']
        read_only_fields = ['user', 'created_at']