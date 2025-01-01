
from rest_framework import serializers
from course.models.blog import Blog
from EStudyApp.serializers import QuestionSetSerializer
from Authentication.serializers import UserSerializer


class BlogSerializer(serializers.ModelSerializer):
    questions_set = QuestionSetSerializer()
    author = UserSerializer()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'author', 'questions_set',
                  'part_info', 'from_ques', 'to_ques', 'created_at', 'updated_at']
