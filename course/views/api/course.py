from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from course.models.course import Course
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import status

from course.serializer.course import CourseDetailSerializer, CourseSerializer


# post create course
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    return Response({'message': 'Course created successfully'})


# get course list
@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True).data
    return Response(serializer, status=status.HTTP_200_OK)


# get course detail
@api_view(['GET'])
@permission_classes([AllowAny])
def course_detail(request, id):
    course = Course.objects.get(id=id)
    serializer = CourseDetailSerializer(course).data
    return Response(serializer, status=status.HTTP_200_OK)
