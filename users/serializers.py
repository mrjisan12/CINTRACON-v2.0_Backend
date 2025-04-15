from rest_framework import serializers
from django.contrib.auth import get_user_model
from cloudinary.uploader import upload
from .models import UserProfile
from django.core.exceptions import ValidationError

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    batch_no = serializers.IntegerField(write_only=True)
    profile_photo = serializers.ImageField(required=False, write_only=True)
    department = serializers.ChoiceField(choices=UserProfile.DEPARTMENTS, write_only=True)  # Add department
    semester = serializers.ChoiceField(choices=UserProfile.SEMESTERS, write_only=True)  # Add semester
    section = serializers.ChoiceField(choices=UserProfile.SECTIONS, write_only=True)  # Add Section


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'batch_no', 'profile_photo', 'department', 'semester','section']

    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        # Remove extra fields that don't belong to User model
        batch_no = validated_data.pop('batch_no')
        profile_photo = validated_data.pop('profile_photo', None)
        department = validated_data.pop('department')
        semester = validated_data.pop('semester')
        section = validated_data.pop('section')
        validated_data.pop('confirm_password')

        # Create user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        # Prepare profile data from validated_data
        profile_data = {
            'user': user,
            'batch_no': batch_no,
            'department': department,
            'semester': semester,
            'section': section,
            'role': validated_data.get('role', 'student'),  # This will now come from form, default is 'student'
            'points': 10 ,
        }

        # Upload profile photo to Cloudinary if provided
        if profile_photo:
            cloudinary_response = upload(profile_photo)
            profile_data['profile_photo'] = cloudinary_response['secure_url']

        # Create UserProfile
        UserProfile.objects.create(**profile_data)

        return user
    
    
class UserProfileSerializer(serializers.ModelSerializer):
    profile_img = serializers.ImageField(required=False)
    cover_photo = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['department', 'semester', 'section', 'points', 'batch_no', 'phone_no', 'blood_grp', 'bio', 'relationship_status', 'role', 'profile_img', 'cover_photo']

    def create(self, validated_data):
        # Handle profile image upload to Cloudinary
        profile_img = validated_data.get('profile_img', None)
        profile_img_url = None
        if profile_img:
            cloudinary_response = upload(profile_img)
            profile_img_url = cloudinary_response['secure_url']  # Cloudinary image URL

        # Ensure the 'user' is passed from the view, not from the validated_data
        user = validated_data.pop('user')

        # Create the user profile
        user_profile = UserProfile.objects.create(
            user=user,  # Now passing the user explicitly
            department=validated_data['department'],
            semester=validated_data['semester'],
            batch_no=validated_data['batch_no'],
            phone_no=validated_data.get('phone_no'),
            blood_grp=validated_data.get('blood_grp'),
            bio=validated_data.get('bio', ''),
            relationship_status=validated_data.get('relationship_status', ''),
            role=validated_data.get('role', 'student'),
            profile_photo=profile_img_url if profile_img else None,
            cover_photo=validated_data.get('cover_photo', None),
            points = 10,
            section = validated_data['section']  # ডিফল্ট 'A'
           
        )
        
        
        return user_profile
    
    
    
    
    
# For Login   
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = User.objects.filter(email=email).first()
        
        if user and user.check_password(password):
            # Login successful - increase points by 5
            try:
                user_profile = UserProfile.objects.get(user=user)
                user_profile.points += 5
                user_profile.save()
            except UserProfile.DoesNotExist:
                # Create user profile if it doesn't exist
                UserProfile.objects.create(user=user, points=5)
            
            return attrs
        
        raise ValidationError('Invalid email or password.')