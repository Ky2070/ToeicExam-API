# from django.shortcuts import render
from django.http import HttpResponse
from .serializers import UserRegistrationSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


# Create your views here.

def auth(request):
    return HttpResponse("Simple JWT for Django")


class UserRegistrationView(APIView):
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"message": "Lỗi server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
