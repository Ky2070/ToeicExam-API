from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from course.models.course import Course
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import status

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from course.serializer.course import CourseDetailSerializer, CourseSerializer

CACHE_TTL = 60 * 5

# post create course
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    return Response({'message': 'Course created successfully'})


class CourseListView(APIView):    
    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(cache_page(CACHE_TTL, key_prefix="course_list"))
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# get course detail
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def course_detail(request, id):
    course = Course.objects.prefetch_related('course_rating').get(id=id)
    serializer = CourseDetailSerializer(course).data
    return Response(serializer, status=status.HTTP_200_OK)


# panel course list