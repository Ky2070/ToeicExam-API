from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from course.models import Lesson, ReviewLesson
from course.serializer.lesson import LessonSerializer, ReviewLessonSerializer


# GET lesson list
@api_view(['GET'])
@permission_classes([AllowAny])
def lesson_list(request):
    lessons = Lesson.objects.all()
    serializer = LessonSerializer(lessons, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# GET lesson detail
@api_view(['GET'])
@permission_classes([AllowAny])
def lesson_detail(request, id):
    try:
        lesson = Lesson.objects.get(id=id)
        serializer = LessonSerializer(lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def review_list_by_lesson(request, lesson_id):
    try:
        reviews = ReviewLesson.objects.filter(lesson_id=lesson_id)
        serializer = ReviewLessonSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
