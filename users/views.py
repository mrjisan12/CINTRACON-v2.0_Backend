
from rest_framework import status
from .utils import api_response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import *
from .serializers import *
from .models import UserVerification
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import random
from datetime import timedelta
from django.template.loader import render_to_string
from .models import UserProfile, UserPoints, CustomUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser



User = get_user_model()

# HTML template for OTP email
def otp_html_template(otp_code):
    return render_to_string('sendOtpEmail.html', {'otp_code': otp_code})

class SendOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = SendOtpSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                otp_code = f"{random.randint(100000, 999999)}"
                expired_at = timezone.now() + timedelta(minutes=5)

                # Save or update OTP
                obj, created = UserVerification.objects.update_or_create(
                    email=email,
                    defaults={
                        'otp_code': otp_code,
                        'expired_at': expired_at,
                    }
                )

                # Send email
                subject = "Your OTP Code"
                from_email = f"CINTRACON <{settings.DEFAULT_FROM_EMAIL}>"
                to = [email]
                text_content = f"Your OTP code is {otp_code}"
                html_content = otp_html_template(otp_code)
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                return api_response(True, 'OTP sent successfully!', 'OTP sent to your email.', 200, status.HTTP_200_OK)
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = CheckOtpSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                otp_code = serializer.validated_data['otp_code']
                try:
                    verification = UserVerification.objects.get(email=email, otp_code=otp_code)
                    if verification.expired_at < timezone.now():
                        return api_response(False, 'OTP expired.', None, 400, status.HTTP_400_BAD_REQUEST)
                    return api_response(True, 'OTP verified successfully!', 'OTP is valid.', 200, status.HTTP_200_OK)
                except UserVerification.DoesNotExist:
                    return api_response(False, 'Invalid OTP or email.', None, 400, status.HTTP_400_BAD_REQUEST)
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = PasswordResetSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                new_password = serializer.validated_data['new_password']
                try:
                    user = User.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    return api_response(True, 'Password reset successfully!', 'Password has been updated.', 200, status.HTTP_200_OK)
                except User.DoesNotExist:
                    return api_response(False, 'User not found.', None, 404, status.HTTP_404_NOT_FOUND)
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
     
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                # Add entry to UserPoints
                UserPoints.objects.create(user=user, points=10)
                refresh = RefreshToken.for_user(user)
                return api_response(True, 'User successfully registered!', {
                    'user': {
                        'full_name': user.full_name,
                        'email': user.email
                    },
                    'accessToken': str(refresh.access_token),
                    'refreshToken': str(refresh)
                }, 201, status.HTTP_201_CREATED)
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)




# For Login
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                user = User.objects.filter(email=email).first()
                userprofile = UserProfile.objects.filter(id=user.id).first()
                if user and user.check_password(password):
                    # Add entry to UserPoints
                    UserPoints.objects.create(user=user, points=5)
                    refresh = RefreshToken.for_user(user)
                    return api_response(True, 'User successfully logged in!', {
                        'full_name': user.full_name,
                        'email': user.email,
                        'department': userprofile.department,
                        'semester': userprofile.semester,
                        'section': userprofile.section,
                        'batch_no': userprofile.batch_no,
                        'points': userprofile.points,
                        'phone_no': userprofile.phone_no,
                        'blood_grp': userprofile.blood_grp,
                        'role': userprofile.role,
                        'accessToken': str(refresh.access_token),
                        'refreshToken': str(refresh)
                    }, 200, status.HTTP_200_OK)
                return api_response(False, 'Invalid credentials', None, 401, status.HTTP_401_UNAUTHORIZED)
            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# For Logout
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Access token long-lived hole backend e blacklist optional
        return api_response(True, "Logged out successfully.",None, status.HTTP_200_OK)
# User Profile Info API

class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                return api_response(False, 'Authentication required', None, 401, status.HTTP_401_UNAUTHORIZED)
            user_profile = UserProfile.objects.get(user=user)
            data = {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'department': user_profile.department,
                'semester': user_profile.semester,
                'section': user_profile.section,
                'batch_no': user_profile.batch_no,
                'points': user_profile.points,
                'phone_no': user_profile.phone_no,
                'blood_grp': user_profile.blood_grp,
                'bio': user_profile.bio,
                'relationship_status': user_profile.relationship_status,
                'role': user_profile.role,
                'is_active': user.is_active,
                'profile_photo': user_profile.profile_photo.url if user_profile.profile_photo else None,
                'cover_photo': user_profile.cover_photo.url if user_profile.cover_photo else None,
                'facebook_link': user_profile.facebook_link,
                'instagram_link': user_profile.instagram_link,
                'linkedin_link': user_profile.linkedin_link,
                'github_link': user_profile.github_link,
            }
            return api_response(True, 'User profile fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# user profile update API
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # supports file or json

    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileUpdateSerializer(
                profile, data=request.data, partial=True, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()

                profile.refresh_from_db()
                user = request.user

                data = {
                    'id': user.id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'department': profile.department,
                    'semester': profile.semester,
                    'section': profile.section,
                    'batch_no': profile.batch_no,
                    'points': profile.points,
                    'phone_no': profile.phone_no,
                    'blood_grp': profile.blood_grp,
                    'bio': profile.bio,
                    'relationship_status': profile.relationship_status,
                    'role': profile.role,
                    'is_active': user.is_active,
                    'profile_photo': profile.profile_photo if isinstance(profile.profile_photo, str) else (profile.profile_photo.url if profile.profile_photo else None),
                    'cover_photo': profile.cover_photo if isinstance(profile.cover_photo, str) else (profile.cover_photo.url if profile.cover_photo else None),
                    'facebook_link': profile.facebook_link,
                    'instagram_link': profile.instagram_link,
                    'linkedin_link': profile.linkedin_link,
                    'github_link': profile.github_link,
                }
                return api_response(True, 'Profile updated successfully!', data, 200, status.HTTP_200_OK)

            return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)

        except UserProfile.DoesNotExist:
            return api_response(False, 'User profile not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)






class UserProfileByIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            data = {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'department': user_profile.department,
                'semester': user_profile.semester,
                'section': user_profile.section,
                'batch_no': user_profile.batch_no,
                'points': user_profile.points,
                'phone_no': user_profile.phone_no,
                'blood_grp': user_profile.blood_grp,
                'bio': user_profile.bio,
                'relationship_status': user_profile.relationship_status,
                'role': user_profile.role,
                'is_active': user.is_active,
                'profile_photo': user_profile.profile_photo.url if user_profile.profile_photo else None,
                'cover_photo': user_profile.cover_photo.url if user_profile.cover_photo else None,
                'facebook_link': user_profile.facebook_link,
                'instagram_link': user_profile.instagram_link,
                'linkedin_link': user_profile.linkedin_link,
                'github_link': user_profile.github_link,
            }
            return api_response(True, 'User profile fetched successfully!', data, 200, status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return api_response(False, 'User not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)