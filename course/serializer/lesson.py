from rest_framework import serializers
from course.models import Lesson, ReviewLesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'video', 'content', 'quiz', 'created_at', 'updated_at']


class ReviewLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLesson
        fields = ['id', 'user', 'lesson', 'content', 'publish_date', 'created_at', 'updated_at']
