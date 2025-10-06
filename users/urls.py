from django.urls import path
from .views import *

urlpatterns = [
    path('register', UserRegistrationView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('send-otp', SendOtpView.as_view(), name='send-otp'),
    path('check-otp', CheckOtpView.as_view(), name='check-otp'),
    path('reset-password', PasswordResetView.as_view(), name='password-reset'),
    path('user-profile', UserProfileView.as_view(), name='user_profile'),
    path('user-profile-by-id/<int:user_id>', UserProfileByIdView.as_view(), name='user_profile_by_id'),
]