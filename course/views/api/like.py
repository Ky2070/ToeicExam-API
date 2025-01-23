from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from course.models.like import LikeBlog
from course.models.blog import Blog
from course.serializer.like import LikeBlogSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_blog(request, blog_id):
    """Toggle like/unlike for a blog"""
    try:
        blog = Blog.objects.get(id=blog_id)
        like, created = LikeBlog.objects.get_or_create(
            user=request.user,
            blog=blog
        )
        
        if not created:
            # If like already existed, remove it (unlike)
            like.delete()
            return Response({
                'status': 'unliked',
                'likes_count': blog.blog_likes.count()
            }, status=status.HTTP_200_OK)
            
        return Response({
            'status': 'liked',
            'likes_count': blog.blog_likes.count()
        }, status=status.HTTP_201_CREATED)
        
    except Blog.DoesNotExist:
        return Response(
            {'error': 'Blog not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_blog_likes(request, blog_id):
    """Get all likes for a blog"""
    try:
        blog = Blog.objects.get(id=blog_id)
        likes = blog.blog_likes.all()
        serializer = LikeBlogSerializer(likes, many=True)
        return Response({
            'likes_count': likes.count(),
            'likes': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Blog.DoesNotExist:
        return Response(
            {'error': 'Blog not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_like(request, blog_id):
    """Check if current user has liked the blog"""
    try:
        liked = LikeBlog.objects.filter(
            user=request.user,
            blog_id=blog_id
        ).exists()
        
        return Response({
            'has_liked': liked
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        ) 