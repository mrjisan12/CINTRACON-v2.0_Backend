from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


class SignupRateThrottle(AnonRateThrottle):
    scope = 'signup'


class OtpRateThrottle(AnonRateThrottle):
    scope = 'otp'


class PostCreateRateThrottle(UserRateThrottle):
    scope = 'post_create'
