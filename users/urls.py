from django.urls import path
from .views import *

urlpatterns = [
    # Auth
    path('signup', UserRegistrationView.as_view(), name='signup'),
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', UserLogoutView.as_view(), name='logout'),

    # Email verification
    path('verify-email', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification', ResendVerificationView.as_view(), name='resend-verification'),

    # OTP / Password reset
    path('send-otp', SendOtpView.as_view(), name='send-otp'),
    path('check-otp', CheckOtpView.as_view(), name='check-otp'),
    path('reset-password', PasswordResetView.as_view(), name='password-reset'),

    # Profile
    path('user-profile', UserProfileView.as_view(), name='user_profile'),
    path('user-profile-update', UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('user-profile-by-id/<int:user_id>', UserProfileByIdView.as_view(), name='user_profile_by_id'),

    # Follow
    path('follow/<int:user_id>/', FollowToggleView.as_view(), name='follow-toggle'),
    path('followers/<int:user_id>/', FollowerListView.as_view(), name='follower-list'),
    path('following/<int:user_id>/', FollowingListView.as_view(), name='following-list'),
]
