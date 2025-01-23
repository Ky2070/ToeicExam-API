from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from course.models import Rating
from course.models.course import Course
from course.serializer.rating import RatingSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_course(request, course_id):
    user = request.user
    point = request.data.get('point')
    if point is None:
        return Response({'message': 'Point is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    course = Course.objects.get(id=course_id)
    if course is None:
        return Response({'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    rating = Rating.objects.filter(user=user, course=course)
    if rating.exists():
        return Response({'message': 'You have already rated this course'}, status=status.HTTP_400_BAD_REQUEST)
    
    rating = Rating.objects.create(user=user, course=course, star=point)
    serializer = RatingSerializer(rating)
    
    return Response(serializer.data, status=status.HTTP_200_OK)