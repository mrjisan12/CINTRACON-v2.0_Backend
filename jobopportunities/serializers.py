from rest_framework import serializers
from .models import JobPost
from cloudinary.uploader import upload
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()



# User serializer to fetch full_name and profile_photo
class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    profile_photo = serializers.CharField(source='profile.profile_photo.url', allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'profile_photo']


class JobPostSerializer(serializers.ModelSerializer):
    
    user = UserProfileSerializer(read_only=True)
    job_post_image = serializers.SerializerMethodField()
    
    class Meta:
        model = JobPost
        fields = ['id', 'title', 'description', 'company_name', 'salary', 'place', 'start_time', 'end_time', 'apply_link', 'job_post_image', 'deadline', 'user' ,'created_at']
        read_only_fields = ['user', 'created_at']  # Prevent modification of created_at or user

    
    def get_job_post_image(self, obj):
        if obj.job_post_image:
            # Remove 'image/upload/' prefix if it exists
            url = str(obj.job_post_image)
            if 'image/upload/' in url:
                url = url.replace('image/upload/', '')
            return url
        return None
    
    def create(self, validated_data):
        user = self.context['request'].user
        job_image = self.context['request'].FILES.get('job_post_image')
        job_image_url = None

        if job_image:
            try:
                cloudinary_response = upload(job_image)
                job_image_url = cloudinary_response.get('secure_url')
            except Exception as e:
                print(f"Error uploading image: {str(e)}")

        job_post = JobPost.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            company_name=validated_data['company_name'],
            salary=validated_data['salary'],
            place=validated_data['place'],
            start_time=validated_data['start_time'],
            end_time=validated_data['end_time'],
            apply_link=validated_data['apply_link'],
            job_post_image=job_image_url,
            deadline=validated_data.get('deadline', None),
            user=user
        )
        return job_post
