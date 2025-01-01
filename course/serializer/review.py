from rest_framework import serializers
from course.models.lesson import ReviewLesson
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ReviewLessonReplySerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = ReviewLesson
        fields = ['id', 'user', 'lesson', 'content', 'publish_date', 'parent']
        read_only_fields = ['publish_date']

class ReviewLessonSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    replies = ReviewLessonReplySerializer(many=True, read_only=True)
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewLesson
        fields = ['id', 'user', 'lesson', 'content', 'publish_date', 'replies', 'reply_count']
        read_only_fields = ['publish_date']

    def get_reply_count(self, obj):
        return obj.replies.count() 