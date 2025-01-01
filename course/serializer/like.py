from rest_framework import serializers
from course.models.like import LikeBlog
from Authentication.serializers import UserSerializer

class LikeBlogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = LikeBlog
        fields = ['id', 'user', 'blog', 'created_at']
        read_only_fields = ['created_at'] 