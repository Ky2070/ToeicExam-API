from django.http import HttpResponse
from .serializers import UserRegistrationSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView


class UserRegistrationView(APIView):
    def post(self, request):
        user = User.objects.filter(email=request.data.get("email"))

        if user.exists():
            return Response(
                {"message": "Email đã tồn tại"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "User registered successfully."},
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(
                {"message": "Lỗi server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLoginView(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid email or password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = authenticate(request, email=user.email, password=password)
            print(user)
            if user is not None:
                # Create new token pair
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                # Store the access token's JTI in the user model
                user.current_jti = str(access_token["jti"])
                user.save()

                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(access_token),
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(e)
            return Response(
                {"message": "Lỗi server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # Get the new access token and extract its JTI
            access_token = AccessToken(response.data["access"])
            user = access_token.payload.get("user_id")

            # Update the user's current_jti
            if user:
                user = User.objects.get(id=user)
                user.current_jti = str(access_token["jti"])
                user.save()

        return response


class UserProfileView(APIView):
    Model = User
    serializer = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserAllView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
