from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from course.models.lesson import ReviewLesson
from course.serializer.review import ReviewLessonSerializer, ReviewLessonReplySerializer

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

CACHE_TTL = 60 * 5

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
@cache_page(CACHE_TTL, key_prefix="lesson_review")
def get_lesson_reviews(request, lesson_id):
    """Get all reviews for a specific lesson"""
    # Only get parent reviews (not replies)
    reviews = ReviewLesson.objects.filter(
        lesson_id=lesson_id,
        parent=None
    ).order_by('-publish_date')
    serializer = ReviewLessonSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, lesson_id):
    """Create a new review for a lesson"""
    data = {
        'lesson': lesson_id,
        'content': request.data.get('content'),
        'user': request.user.id
    }
    
    serializer = ReviewLessonSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_to_review(request, review_id):
    """Create a reply to an existing review"""
    try:
        parent_review = ReviewLesson.objects.get(id=review_id)
    except ReviewLesson.DoesNotExist:
        return Response(
            {'error': 'Parent review not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    data = {
        'lesson': parent_review.lesson.id,
        'content': request.data.get('content'),
        'parent': parent_review.id
    }
    
    serializer = ReviewLessonReplySerializer(data=data)
    if serializer.is_valid():
        serializer.save(
            user=request.user,
            lesson=parent_review.lesson,
            parent=parent_review
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_review(request, review_id):
    """Update or delete a review"""
    try:
        review = ReviewLesson.objects.get(id=review_id, user=request.user)
    except ReviewLesson.DoesNotExist:
        return Response(
            {'error': 'Review not found or you do not have permission'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        serializer = (
            ReviewLessonReplySerializer if review.parent 
            else ReviewLessonSerializer
        )(review, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 