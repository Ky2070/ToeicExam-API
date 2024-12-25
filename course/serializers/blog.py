from rest_framework import serializers
from course.models.blog import Blog, CommentBlog
from course.serializers.base import BaseSerializer, BaseResponseSerializer, BaseListSerializer
from Authentication.serializers import UserSerializer
from EStudyApp.serializers import QuestionSetSerializer

class CommentBlogSerializer(BaseSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta(BaseSerializer.Meta):
        model = CommentBlog
        fields = BaseSerializer.Meta.fields + [
            'user',
            'blog',
            'parent',
            'content',
            'publish_date',
            'replies'
        ]

    def get_replies(self, obj):
        if hasattr(obj, 'replies'):
            return CommentBlogSerializer(obj.replies.all(), many=True).data
        return []

class BlogSerializer(BaseSerializer):
    author = UserSerializer(read_only=True)
    questions_set = QuestionSetSerializer(read_only=True)
    comments = CommentBlogSerializer(source='commentblog_blog', many=True, read_only=True)
    
    class Meta(BaseSerializer.Meta):
        model = Blog
        fields = BaseSerializer.Meta.fields + [
            'title',
            'content',
            'part_info',
            'from_ques',
            'to_ques',
            'author',
            'questions_set',
            'is_published',
            'comments'
        ]

    def __init__(self, *args, **kwargs):
        # Pop 'include_comments' from kwargs
        include_comments = kwargs.pop('include_comments', False)
        super().__init__(*args, **kwargs)
        
        # Remove comments field if not needed
        if not include_comments:
            self.fields.pop('comments', None)

    def validate_title(self, value):
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long")
        return value.strip()

    def validate_content(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long")
        return value.strip()

class BlogResponseSerializer(BaseResponseSerializer):
    author = UserSerializer(read_only=True)
    questions_set = QuestionSetSerializer(read_only=True)
    
    class Meta(BaseResponseSerializer.Meta):
        model = Blog
        fields = BaseResponseSerializer.Meta.fields + [
            'title',
            'content',
            'part_info',
            'from_ques',
            'to_ques',
            'author',
            'questions_set',
            'publish_date'
        ]

class BlogListSerializer(BaseSerializer):
    """Serializer for listing blogs without comments"""
    author = UserSerializer(read_only=True)
    questions_set = QuestionSetSerializer(read_only=True)
    
    class Meta(BaseSerializer.Meta):
        model = Blog
        fields = BaseSerializer.Meta.fields + [
            'title',
            'content',
            'part_info',
            'from_ques',
            'to_ques',
            'author',
            'questions_set',
            'is_published'
        ]

class BlogDetailWithCommentsSerializer(BlogListSerializer):
    """Serializer for blog detail with comments"""
    comments = CommentBlogSerializer(source='commentblog_blog', many=True, read_only=True)
    
    class Meta(BlogListSerializer.Meta):
        fields = BlogListSerializer.Meta.fields + ['comments']

class BlogCreateUpdateSerializer(BlogSerializer):
    """Serializer for creating and updating blogs"""
    class Meta(BlogSerializer.Meta):
        model = Blog
        fields = BlogSerializer.Meta.fields
        read_only_fields = BlogSerializer.Meta.read_only_fields + [
            'author',
            'publish_date'
        ]

    def create(self, validated_data):
        # Get the current user from the context
        user = self.context['request'].user
        validated_data['author'] = user
        return super().create(validated_data)
