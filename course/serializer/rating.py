
from rest_framework import serializers
from course.models.rating import Rating
from course.serializer.course import CourseSerializer
from Authentication.serializers import UserSerializer


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    course = CourseSerializer()
    
    class Meta:
        model = Rating
        fields = ['id', 'user', 'course', 'star']