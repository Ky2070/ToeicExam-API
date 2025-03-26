from rest_framework import serializers
from course.models.blog import Blog
from EStudyApp.serializers import QuestionSetSerializer
from Authentication.serializers import UserSerializer


class BlogSerializer(serializers.ModelSerializer):
    questions_set = QuestionSetSerializer()
    author = UserSerializer()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'author', 'questions_set',
                  'part_info', 'from_ques', 'to_ques', 'created_at', 'updated_at',
                  'likes_count', 'has_liked', 'is_published', 'status']

    def get_likes_count(self, obj):
        return obj.blog_likes.count()
    
    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.blog_likes.filter(user=request.user).exists()
        return False
