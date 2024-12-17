from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from course.models.course import Course
from rest_framework.permissions import IsAuthenticated

# post create course
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    return Response({'message': 'Course created successfully'})
