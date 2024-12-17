from rest_framework import serializers
from course.models.course import Course

# course serializer
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'level', 'duration', 'info', 'target', 'cover', 'banner', 'updated_at', 'created_at']
        

class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'level', 'duration', 'info', 'target', 'cover', 'banner', 'updated_at', 'created_at']
