from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

User = get_user_model()

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
     
    def post(self, request):
        # Step 1: Validate and create the user
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Step 2: Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                'msg': 'User successfully registered!',
                'success': True,
                'data': {
                    'refreshToken': str(refresh),
                    'accessToken': str(refresh.access_token)
                },
                'code': 201
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# For Login
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Step 1: Validate and authenticate user
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Step 2: Authenticate user
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                # Step 3: Generate JWT token
                refresh = RefreshToken.for_user(user)
                return Response({
                    'msg': 'User successfully logged in!',
                    'success': True,
                    'data': {
                        'refreshToken': str(refresh),
                        'accessToken': str(refresh.access_token)
                    },
                    'code': 200
                })
            
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)