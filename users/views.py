import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from home.models import Post
from home.serializers import PostSerializer
from .exceptions import custom_exception_handler  # noqa — imported for settings reference
from .models import UserVerification, UserProfile, UserPoints, CustomUser, Follow
from .serializers import *
from .throttles import LoginRateThrottle, SignupRateThrottle, OtpRateThrottle
from .utils import api_response

User = get_user_model()


def _otp_html(otp_code):
    return render_to_string('sendOtpEmail.html', {'otp_code': otp_code})


def _make_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)


def _user_data(user, userprofile, access_token=None, refresh_token=None):
    data = {
        'id': user.id,
        'name': user.full_name,
        'full_name': user.full_name,
        'email': user.email,
        'role': userprofile.role,
        'is_admin': userprofile.is_admin,
        'is_email_verified': user.is_email_verified,
        'is_active': user.is_active,
        'department': userprofile.department,
        'semester': userprofile.semester,
        'section': userprofile.section,
        'batch_no': userprofile.batch_no,
        'points': userprofile.points,
        'phone_no': userprofile.phone_no,
        'blood_grp': userprofile.blood_grp,
        'bio': userprofile.bio,
        'relationship_status': userprofile.relationship_status,
        'profile_photo': userprofile.profile_photo.url if userprofile.profile_photo else None,
        'cover_photo': userprofile.cover_photo.url if userprofile.cover_photo else None,
        'facebook_link': userprofile.facebook_link,
        'instagram_link': userprofile.instagram_link,
        'linkedin_link': userprofile.linkedin_link,
        'github_link': userprofile.github_link,
    }
    if access_token:
        data['accessToken'] = access_token
        data['refreshToken'] = refresh_token
    return data


def _send_otp_email(email, otp_code):
    """Sends OTP via Celery if available, otherwise synchronously."""
    try:
        from .tasks import send_verification_email
        send_verification_email.delay(email, otp_code)
    except Exception:
        subject = "Your OTP Code - CINTRACON"
        from_email = f"CINTRACON <{settings.DEFAULT_FROM_EMAIL}>"
        msg = EmailMultiAlternatives(subject, f"Your OTP: {otp_code}", from_email, [email])
        try:
            msg.attach_alternative(_otp_html(otp_code), "text/html")
        except Exception:
            pass
        msg.send(fail_silently=True)


# ─── OTP ─────────────────────────────────────────────────────────────────────

class SendOtpView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpRateThrottle]

    def post(self, request):
        try:
            serializer = SendOtpSerializer(data=request.data)
            if not serializer.is_valid():
                return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data['email']
            otp_code = f"{random.randint(100000, 999999)}"
            expired_at = timezone.now() + timedelta(minutes=10)

            UserVerification.objects.filter(email=email).delete()
            UserVerification.objects.create(email=email, otp_code=otp_code, expired_at=expired_at)
            _send_otp_email(email, otp_code)
            return api_response(True, 'OTP sent successfully!', None, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = CheckOtpSerializer(data=request.data)
            if not serializer.is_valid():
                return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            try:
                verification = UserVerification.objects.get(email=email, otp_code=otp_code)
                if verification.expired_at < timezone.now():
                    return api_response(False, 'OTP expired.', None, 400, status.HTTP_400_BAD_REQUEST)
                return api_response(True, 'OTP verified successfully!', None, 200, status.HTTP_200_OK)
            except UserVerification.DoesNotExist:
                return api_response(False, 'Invalid OTP or email.', None, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = PasswordResetSerializer(data=request.data)
            if not serializer.is_valid():
                return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                return api_response(True, 'Password reset successfully!', None, 200, status.HTTP_200_OK)
            except User.DoesNotExist:
                return api_response(False, 'User not found.', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SignupRateThrottle]

    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if not serializer.is_valid():
                return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            UserPoints.objects.create(user=user, points=10)

            # Generate verification OTP
            otp_code = f"{random.randint(100000, 999999)}"
            expired_at = timezone.now() + timedelta(minutes=10)
            UserVerification.objects.filter(email=user.email).delete()
            UserVerification.objects.create(email=user.email, otp_code=otp_code, expired_at=expired_at)
            _send_otp_email(user.email, otp_code)

            return api_response(True, 'Registration successful! Check your email for OTP verification.', None, 201, status.HTTP_201_CREATED)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email', '').strip()
            otp_code = request.data.get('otp', '').strip()

            if not email or not otp_code:
                return api_response(False, 'email and otp are required.', None, 400, status.HTTP_400_BAD_REQUEST)

            try:
                verification = UserVerification.objects.get(email=email, otp_code=otp_code)
            except UserVerification.DoesNotExist:
                return api_response(False, 'Invalid OTP or email.', None, 400, status.HTTP_400_BAD_REQUEST)

            if verification.expired_at < timezone.now():
                return api_response(False, 'OTP has expired. Please request a new one.', None, 400, status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=email).first()
            if not user:
                return api_response(False, 'User not found.', None, 404, status.HTTP_404_NOT_FOUND)

            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
            verification.delete()

            # Auto-login after verification
            userprofile = UserProfile.objects.filter(user=user).first()
            access_token, refresh_token = _make_token(user)

            data = _user_data(user, userprofile, access_token, refresh_token) if userprofile else {
                'id': user.id, 'email': user.email, 'accessToken': access_token, 'refreshToken': refresh_token
            }
            return api_response(True, 'Email verified successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpRateThrottle]

    def post(self, request):
        try:
            email = request.data.get('email', '').strip()
            if not email:
                return api_response(False, 'email is required.', None, 400, status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=email).first()
            if not user:
                return api_response(False, 'No account found with this email.', None, 404, status.HTTP_404_NOT_FOUND)

            if user.is_email_verified:
                return api_response(False, 'Email is already verified.', None, 400, status.HTTP_400_BAD_REQUEST)

            otp_code = f"{random.randint(100000, 999999)}"
            expired_at = timezone.now() + timedelta(minutes=10)
            UserVerification.objects.filter(email=email).delete()
            UserVerification.objects.create(email=email, otp_code=otp_code, expired_at=expired_at)
            _send_otp_email(email, otp_code)
            return api_response(True, 'Verification OTP sent!', None, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = User.objects.filter(email=email).first()

            if not user or not user.check_password(password):
                return api_response(False, 'Invalid credentials', None, 401, status.HTTP_401_UNAUTHORIZED)

            if not user.is_email_verified:
                return api_response(False, 'Please verify your email before logging in.', {'email': email}, 401, status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return api_response(False, 'Your account has been deactivated. Please contact admin.', None, 403, status.HTTP_403_FORBIDDEN)

            userprofile = UserProfile.objects.filter(user=user).first()
            UserPoints.objects.create(user=user, points=5)
            access_token, refresh_token = _make_token(user)

            return api_response(True, 'Login successful!', _user_data(user, userprofile, access_token, refresh_token), 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return api_response(True, 'Logged out successfully.', None, 200, status.HTTP_200_OK)


# ─── Profile ─────────────────────────────────────────────────────────────────

class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                return api_response(False, 'Authentication required', None, 401, status.HTTP_401_UNAUTHORIZED)

            user_profile = UserProfile.objects.get(user=user)
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))

            posts = Post.objects.filter(user=user).order_by('-created_at')
            total_posts = posts.count()
            start = (page - 1) * size
            paginated_posts = posts[start:start + size]

            data = _user_data(user, user_profile)
            data['posts'] = PostSerializer(paginated_posts, many=True, context={'request': request}).data
            data['total_posts'] = total_posts
            data['followers_count'] = user.followers.count()
            data['following_count'] = user.following.count()
            return api_response(True, 'User profile fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True, context={'request': request})
            if not serializer.is_valid():
                return api_response(False, 'Validation error', serializer.errors, 400, status.HTTP_400_BAD_REQUEST)

            serializer.save()
            profile.refresh_from_db()
            user = request.user

            data = _user_data(user, profile)
            return api_response(True, 'Profile updated successfully!', data, 200, status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return api_response(False, 'User profile not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileByIdView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))

            posts = Post.objects.filter(user=user).order_by('-created_at')
            total_posts = posts.count()
            start = (page - 1) * size
            paginated_posts = posts[start:start + size]

            viewer = request.user
            is_following = (
                viewer.is_authenticated and
                Follow.objects.filter(follower=viewer, following=user).exists()
            )

            data = _user_data(user, user_profile)
            data['posts'] = PostSerializer(paginated_posts, many=True, context={'request': request}).data
            data['total_posts'] = total_posts
            data['followers_count'] = user.followers.count()
            data['following_count'] = user.following.count()
            data['is_following'] = is_following
            return api_response(True, 'User profile fetched successfully!', data, 200, status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return api_response(False, 'User not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Follow ──────────────────────────────────────────────────────────────────

class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            if request.user.id == user_id:
                return api_response(False, 'You cannot follow yourself.', None, 400, status.HTTP_400_BAD_REQUEST)

            target = CustomUser.objects.get(id=user_id)
            follow_obj = Follow.objects.filter(follower=request.user, following=target)
            if follow_obj.exists():
                follow_obj.delete()
                msg = 'Unfollowed successfully.'
                is_following = False
            else:
                Follow.objects.create(follower=request.user, following=target)
                msg = 'Followed successfully.'
                is_following = True

                # Send notification
                try:
                    from notifications.utils import create_notification
                    create_notification(
                        recipient=target,
                        sender=request.user,
                        notif_type='follow',
                        message=f'{request.user.full_name} started following you.',
                        link=f'/profile/{request.user.id}',
                    )
                except Exception:
                    pass

            return api_response(True, msg, {
                'is_following': is_following,
                'followers_count': target.followers.count(),
            }, 200, status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return api_response(False, 'User not found.', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class FollowerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            followers = Follow.objects.filter(following=user).select_related('follower__profile')
            data = [
                {
                    'id': f.follower.id,
                    'name': f.follower.full_name,
                    'profile_photo': f.follower.profile.profile_photo.url if f.follower.profile.profile_photo else None,
                    'department': f.follower.profile.department,
                }
                for f in followers
            ]
            return api_response(True, 'Followers fetched.', data, 200, status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return api_response(False, 'User not found.', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            following = Follow.objects.filter(follower=user).select_related('following__profile')
            data = [
                {
                    'id': f.following.id,
                    'name': f.following.full_name,
                    'profile_photo': f.following.profile.profile_photo.url if f.following.profile.profile_photo else None,
                    'department': f.following.profile.department,
                }
                for f in following
            ]
            return api_response(True, 'Following fetched.', data, 200, status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return api_response(False, 'User not found.', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
