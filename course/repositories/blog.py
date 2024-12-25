# blog repository
from typing import Dict, Any, List, Optional, Tuple
from django.utils import timezone
from django.db.models import Q
from course.models.blog import Blog
from course.repositories.base import OrderBy, Pagination
from course.serializers.blog import BlogSerializer, BlogListSerializer

class BlogOrderBy(OrderBy):
    _allows_fields = (
        "id", "-id",
        "title", "-title",
        "created_at", "-created_at",
        "updated_at", "-updated_at",
    )
    _default_order_by = ("created_at",)

class BlogQuery:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.id__in = kwargs.get('id__in')
        self.id__not_in = kwargs.get('id__not_in')
        
        self.title = kwargs.get('title')
        self.title__contains = kwargs.get('title__contains') 
        self.title__icontains = kwargs.get('title__icontains')
        self.title__startswith = kwargs.get('title__startswith')
        self.title__endswith = kwargs.get('title__endswith')
        
        self.content = kwargs.get('content')
        self.content__contains = kwargs.get('content__contains')
        self.content__icontains = kwargs.get('content__icontains')
        
        self.part_info = kwargs.get('part_info')
        self.from_ques = kwargs.get('from_ques')
        self.to_ques = kwargs.get('to_ques')
        
        self.created_at = kwargs.get('created_at')
        self.created_at__gte = kwargs.get('created_at__gte')
        self.created_at__lte = kwargs.get('created_at__lte')
        
        self.updated_at = kwargs.get('updated_at')
        self.updated_at__gte = kwargs.get('updated_at__gte')
        self.updated_at__lte = kwargs.get('updated_at__lte')
        
        self.order_by = kwargs.get('order_by')
        
        self.is_published = kwargs.get('is_published')
        self.is_published__in = kwargs.get('is_published__in')

    def build_query(self) -> Q:
        query = Q()
        
        if self.id:
            query &= Q(id=self.id)
        if self.id__in:
            query &= Q(id__in=self.id__in)
        if self.id__not_in:
            query &= ~Q(id__in=self.id__not_in)
            
        if self.title:
            query &= Q(title=self.title)
        if self.title__contains:
            query &= Q(title__contains=self.title__contains)
        if self.title__icontains:
            query &= Q(title__icontains=self.title__icontains)
        if self.title__startswith:
            query &= Q(title__startswith=self.title__startswith)
        if self.title__endswith:
            query &= Q(title__endswith=self.title__endswith)
            
        if self.content__contains:
            query &= Q(content__contains=self.content__contains)
        if self.content__icontains:
            query &= Q(content__icontains=self.content__icontains)
            
        if self.part_info:
            query &= Q(part_info=self.part_info)
        if self.from_ques:
            query &= Q(from_ques=self.from_ques)
        if self.to_ques:
            query &= Q(to_ques=self.to_ques)

        if self.created_at:
            query &= Q(created_at=self.created_at)
        if self.created_at__gte:
            query &= Q(created_at__gte=self.created_at__gte)
        if self.created_at__lte:
            query &= Q(created_at__lte=self.created_at__lte)

        if self.updated_at:
            query &= Q(updated_at=self.updated_at)
        if self.updated_at__gte:
            query &= Q(updated_at__gte=self.updated_at__gte)
        if self.updated_at__lte:
            query &= Q(updated_at__lte=self.updated_at__lte)

        if self.is_published is not None:
            query &= Q(is_published=self.is_published)
        if self.is_published__in:
            query &= Q(is_published__in=self.is_published__in)

        return query

class BlogRepository:
    @staticmethod
    def create_one(blog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single blog record and return serialized data"""
        blog = Blog.objects.create(**blog_data)
        return BlogListSerializer(blog).data

    @staticmethod 
    def create_many(blog_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple blog records and return serialized data"""
        blogs = Blog.objects.bulk_create([Blog(**data) for data in blog_list])
        return BlogSerializer(blogs, many=True).data

    @staticmethod
    def get_one(q: BlogQuery) -> Optional[Dict[str, Any]]:
        """Get a single blog by query and return serialized data"""
        try:
            query = Blog.objects.filter(deleted_at__isnull=True)
            
            if q.id:
                query = query.filter(id=q.id)
            
            # Add select_related for better performance    
            blog = query.select_related('author', 'questions_set').first()
            if blog:
                return BlogListSerializer(blog).data
            return None
            
        except Blog.DoesNotExist:
            return None

    @staticmethod
    def get_list(q: BlogQuery, p: Pagination) -> Tuple[List[Dict[str, Any]], int]:
        """Get a list of blogs with pagination and return serialized data"""
        query = Blog.objects.filter(deleted_at__isnull=True)

        # Build query filters
        if q.id__in:
            query = query.filter(id__in=q.id__in)
        if q.id__not_in:
            query = query.filter(~Q(id__in=q.id__not_in))
            
        if q.title:
            query = query.filter(title=q.title)
        if q.title__contains:
            query = query.filter(title__contains=q.title__contains)
        if q.title__icontains:
            query = query.filter(title__icontains=q.title__icontains)
        if q.title__startswith:
            query = query.filter(title__startswith=q.title__startswith)
        if q.title__endswith:
            query = query.filter(title__endswith=q.title__endswith)
            
        if q.content__contains:
            query = query.filter(content__contains=q.content__contains)
        if q.content__icontains:
            query = query.filter(content__icontains=q.content__icontains)
            
        if q.part_info:
            query = query.filter(part_info=q.part_info)
        if q.from_ques:
            query = query.filter(from_ques=q.from_ques)
        if q.to_ques:
            query = query.filter(to_ques=q.to_ques)

        if q.created_at:
            query = query.filter(created_at=q.created_at)
        if q.created_at__gte:
            query = query.filter(created_at__gte=q.created_at__gte)
        if q.created_at__lte:
            query = query.filter(created_at__lte=q.created_at__lte)

        # Get total count
        total = query.count()

        # Apply ordering
        order_by = BlogOrderBy(q.order_by)
        query = query.order_by(*order_by.fields)

        # Add select_related for better performance
        query = query.select_related('author', 'questions_set')

        # Apply pagination
        blogs = query[p.offset:p.offset + p.limit]

        # Serialize the data
        serialized_data = BlogListSerializer(blogs, many=True).data

        return serialized_data, total

    @staticmethod
    def update(blog_id: int, data: Dict[str, Any]) -> Tuple[int, Optional[Dict[str, Any]]]:
        """Update a blog record and return serialized data"""
        if 'updated_at' not in data:
            data['updated_at'] = timezone.now()
            
        affected_rows = Blog.objects.filter(id=blog_id).update(**data)
        
        serialized_data = None
        if affected_rows > 0:
            blog = Blog.objects.select_related('author', 'questions_set').get(id=blog_id)
            serialized_data = BlogListSerializer(blog).data
            
        return affected_rows, serialized_data

    @staticmethod
    def delete(blog_id: int) -> int:
        """Soft delete a blog record"""
        return Blog.objects.filter(id=blog_id).update(deleted_at=timezone.now())

    @staticmethod
    def delete_many(blog_ids: List[int]) -> int:
        """Soft delete multiple blog records"""
        return Blog.objects.filter(id__in=blog_ids).update(deleted_at=timezone.now())
    
    
# build order
