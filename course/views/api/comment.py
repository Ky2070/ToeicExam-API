from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from course.models.blog import CommentBlog
from course.serializer.comment import CommentBlogSerializer, CommentReplySerializer


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_blog_comments(request, blog_id):
    """Get all comments for a specific blog"""
    comments = CommentBlog.objects.filter(
        blog_id=blog_id,
        parent=None
    ).order_by('-publish_date')
    serializer = CommentBlogSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, blog_id):
    """Create a new comment for a blog"""
    data = {
        'blog': blog_id,
        'content': request.data.get('content')
    }
    
    serializer = CommentBlogSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_to_comment(request, comment_id):
    """Create a reply to an existing comment"""
    try:
        parent_comment = CommentBlog.objects.get(id=comment_id)
    except CommentBlog.DoesNotExist:
        return Response(
            {'error': 'Parent comment not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    data = {
        'blog': parent_comment.blog.id,
        'content': request.data.get('content')
    }
    
    serializer = CommentReplySerializer(data=data)
    if serializer.is_valid():
        serializer.save(
            user=request.user,
            blog=parent_comment.blog,
            parent=parent_comment
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_comment(request, comment_id):
    """Update or delete a comment"""
    try:
        comment = CommentBlog.objects.get(id=comment_id, user=request.user)
    except CommentBlog.DoesNotExist:
        return Response(
            {'error': 'Comment not found or you do not have permission'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        serializer = (
            CommentReplySerializer if comment.parent 
            else CommentBlogSerializer
        )(comment, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 