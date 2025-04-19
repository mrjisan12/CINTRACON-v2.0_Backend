from rest_framework import serializers
from .models import Note
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


class NoteSerializer(serializers.ModelSerializer):
    
    user = UserProfileSerializer(read_only=True)
    note_file = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['uploaded_at']
        
    def get_note_file(self, obj):
        if obj.note_file:
            # Remove 'raw/upload/' prefix if it exists
            url = str(obj.note_file)
            if 'raw/upload/' in url:
                url = url.replace('raw/upload/', '')
            # Add .pdf extension if it's missing
            if not url.endswith('.pdf'):
                url += '.pdf'
            return url
        return None

    def validate(self, data):
        note_file = self.context['request'].FILES.get('note_file')
        drive_link = data.get('drive_link')

        if not note_file and not drive_link:
            raise serializers.ValidationError("Please upload a file or provide a drive link.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        note_file = self.context['request'].FILES.get('note_file')
        file_url = None

        if note_file:
            try:
                cloudinary_response = upload(note_file, resource_type='raw')
                file_url = cloudinary_response.get('secure_url')
            except Exception as e:
                print(f"Cloudinary error: {str(e)}")

        note = Note.objects.create(
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            note_file=file_url,
            drive_link=validated_data.get('drive_link'),
            department=validated_data['department'],
            semester=validated_data['semester'],
            section=validated_data['section'],
            user=user,
        )
        return note
