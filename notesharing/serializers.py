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
    total_downloads = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['uploaded_at', 'total_downloads', 'user']
        
    def get_note_file(self, obj):
        if obj.note_file:
            url = str(obj.note_file)
            
            # Fix Cloudinary URL format for raw files
            if 'res.cloudinary.com' in url:
                # Check if it's missing the proper path structure
                if '/v' in url and '/raw/upload/' not in url:
                    # Convert Cloudinary raw file URLs to include /raw/upload/ after the cloud name.
                    parts = url.split('/v')
                    if len(parts) == 2:
                        base = parts[0]
                        version_and_file = parts[1]
                        url = f"{base}/raw/upload/v{version_and_file}"
                
                # Remove any existing fl_attachment parameter (causing 401)
                if 'fl_attachment' in url:
                    url = url.split('?')[0]  # Remove query parameters
                    
            return url
        return None

    def validate(self, data):
        note_file = self.context['request'].FILES.get('note_file')
        drive_link = data.get('drive_link')

        # Only validate during creation, not during update
        if self.instance is None and not note_file and not drive_link:
            raise serializers.ValidationError("Please upload a file or provide a drive link.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        note_file = self.context['request'].FILES.get('note_file')
        file_url = None

        if note_file:
            try:
                # Upload with simple configuration (remove flags that cause issues)
                cloudinary_response = upload(
                    note_file, 
                    resource_type='raw',
                    use_filename=True,
                    unique_filename=True,
                    overwrite=True,
                    folder="notes"
                    # Remove 'flags' parameter that might cause issues
                )
                file_url = cloudinary_response.get('secure_url')
                print(f"Uploaded file URL: {file_url}")
            except Exception as e:
                print(f"Cloudinary error: {str(e)}")
                raise serializers.ValidationError(f"File upload failed: {str(e)}")

        note = Note.objects.create(
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            note_file=file_url,
            drive_link=validated_data.get('drive_link'),
            department=validated_data['department'],
            semester=validated_data['semester'],
            section=validated_data.get('section', ''),
            user=user,
        )
        return note

    def update(self, instance, validated_data):
        # Handle file upload if a new file is provided
        note_file = self.context['request'].FILES.get('note_file')
        
        if note_file:
            try:
                # Upload new file to Cloudinary
                cloudinary_response = upload(
                    note_file, 
                    resource_type='raw',
                    use_filename=True,
                    unique_filename=True,
                    overwrite=True,
                    folder="notes"
                )
                file_url = cloudinary_response.get('secure_url')
                instance.note_file = file_url
            except Exception as e:
                print(f"Cloudinary error during update: {str(e)}")
                raise serializers.ValidationError(f"File upload failed: {str(e)}")
        
        # Update other fields
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.drive_link = validated_data.get('drive_link', instance.drive_link)
        instance.department = validated_data.get('department', instance.department)
        instance.semester = validated_data.get('semester', instance.semester)
        instance.section = validated_data.get('section', instance.section)
        
        instance.save()
        return instance
