from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from django.core.exceptions import ValidationError
from course.repositories.blog import BlogRepository, BlogQuery
from course.repositories.base import Pagination
from EStudyApp.models import QuestionSet, Question

def normalize_answers(answers: Dict[str, str]) -> Dict[str, str]:
    """Convert answer keys to uppercase"""
    if not answers:
        return {}
    return {k.upper(): v for k, v in answers.items()}

class BlogService:
    def __init__(self):
        self.blog_repository = BlogRepository()

    def get_blog_list(self, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get list of blogs with filters and pagination
        
        Args:
            filters: Dictionary containing filter parameters
                - search: Search in title and content
                - title: Filter by exact title
                - title__contains: Filter by title contains
                - title__icontains: Filter by title contains (case insensitive)
                - content__contains: Filter by content contains
                - content__icontains: Filter by content contains (case insensitive)
                - part_info: Filter by part info
                - from_ques: Filter by from question number
                - to_ques: Filter by to question number
                - created_at__gte: Filter by created date greater than
                - created_at__lte: Filter by created date less than
                - order_by: Order results by field (e.g. "-created_at" for descending)
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary containing:
                - data: List of serialized blog data
                - total: Total number of items
                - page: Current page number
                - total_pages: Total number of pages
                - has_next: Whether there is a next page
                - has_prev: Whether there is a previous page
        """
        # Initialize query params
        query_params = {}
        
        if filters:
            # Handle search across title and content
            if 'search' in filters:
                search_term = filters['search']
                query_params['title__icontains'] = search_term
                query_params['content__icontains'] = search_term

            # Handle exact title match
            if 'title' in filters:
                query_params['title'] = filters['title']

            # Handle title contains
            if 'title__contains' in filters:
                query_params['title__contains'] = filters['title__contains']
            if 'title__icontains' in filters:
                query_params['title__icontains'] = filters['title__icontains']

            # Handle content contains
            if 'content__contains' in filters:
                query_params['content__contains'] = filters['content__contains']
            if 'content__icontains' in filters:
                query_params['content__icontains'] = filters['content__icontains']

            # Handle part info filters
            if 'part_info' in filters:
                query_params['part_info'] = filters['part_info']
            if 'from_ques' in filters:
                query_params['from_ques'] = filters['from_ques']
            if 'to_ques' in filters:
                query_params['to_ques'] = filters['to_ques']

            # Handle date range filters
            if 'created_at__gte' in filters:
                query_params['created_at__gte'] = filters['created_at__gte']
            if 'created_at__lte' in filters:
                query_params['created_at__lte'] = filters['created_at__lte']

            # Handle ordering
            if 'order_by' in filters:
                # Support ordering by is_published
                order_by = filters['order_by']
                if order_by in ['is_published', '-is_published']:
                    query_params['order_by'] = order_by

            # Handle is_published filter
            is_published = filters.get('is_published') or filters.get('isPublished')
            if is_published is not None:
                # Convert string to boolean properly
                if isinstance(is_published, str):
                    is_published = is_published.lower() == 'true'
                # Debug log
                # print(f"Service is_published value: {is_published}, type: {type(is_published)}")
                query_params['is_published'] = is_published

        # Create query object
        query = BlogQuery(**query_params)
        
        # Create pagination object
        pagination = Pagination(page=page, per_page=per_page)
        
        # Get data from repository
        items, total = self.blog_repository.get_list(query, pagination)
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            'data': items,
            'total': total,
            'page': page,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_prev': has_prev,
            'per_page': per_page
        }

    def get_blog_detail(self, blog_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detail of a specific blog
        
        Args:
            blog_id: ID of the blog to retrieve
            
        Returns:
            Serialized blog data or None if not found
        """
        query = BlogQuery(id=blog_id)
        return self.blog_repository.get_one(query)

    def create_blog(self, data: Dict[str, Any], author: Any) -> Dict[str, Any]:
        """
        Create a new blog with question set
        
        Args:
            data: Dictionary containing blog and question set data
            author: User object who is creating the blog
        """
        # Validate required fields
        if not data.get('title'):
            raise ValidationError('Title is required')
        if not data.get('content'):
            raise ValidationError('Content is required')

        try:
            # Handle QuestionSet creation
            questions_set = None
            if 'questions_set' in data:
                questions_set_data = data['questions_set']
                
                # Create QuestionSet with from_ques and to_ques
                questions_set = QuestionSet.objects.create(
                    page=questions_set_data.get('page'),
                    audio=questions_set_data.get('audio'),
                    image=questions_set_data.get('image'),
                    from_ques=data.get('from_ques'),  # Get from blog data
                    to_ques=data.get('to_ques')       # Get from blog data
                )
                
                # Create Questions if provided
                if 'questions' in questions_set_data:
                    for question_data in questions_set_data['questions']:
                        # Normalize answers before saving
                        answers = normalize_answers(question_data.get('answers', {}))
                        
                        Question.objects.create(
                            question_set=questions_set,
                            question_number=question_data.get('question_number'),
                            question_text=question_data.get('question_text'),
                            correct_answer=question_data.get('correct_answer', '').upper(),  # Also uppercase correct_answer
                            difficulty_level=question_data.get('difficulty_level', ''),
                            answers=answers
                        )

            # Prepare blog data
            blog_data = {
                'title': data['title'].strip(),
                'content': data['content'].strip(),
                'author': author,
                'questions_set': questions_set,
                'is_published': data.get('is_published', False)  # Default False nếu không được cung cấp
            }

            # Add optional blog fields
            optional_fields = ['part_info', 'from_ques', 'to_ques']
            for field in optional_fields:
                if field in data:
                    blog_data[field] = data[field]

            # Create blog using repository
            created_blog = self.blog_repository.create_one(blog_data)
            return created_blog

        except Exception as e:
            # Cleanup if error occurs
            if questions_set:
                questions_set.delete()
            raise ValidationError(f'Failed to create blog: {str(e)}')

    def update_blog(self, id: int, data: Dict[str, Any], author: Any) -> Dict[str, Any]:
        """
        Update an existing blog and its question set
        
        Args:
            id: ID of blog to update
            data: Dictionary containing updated blog and question set data
            author: User object who is updating the blog
        """
        try:
            # Get existing blog
            blog_data = self.blog_repository.get_one(BlogQuery(id=id))
            if not blog_data:
                raise ValidationError('Blog not found')

            # Check ownership unless user is teacher
            if not author.is_teacher and blog_data['author']['id'] != author.id:
                raise ValidationError("You don't have permission to edit this blog")

            # Prepare update data
            update_data = {}
            
            # Update blog fields
            if 'title' in data:
                update_data['title'] = data['title'].strip()
            if 'content' in data:
                update_data['content'] = data['content'].strip()
            if 'part_info' in data:
                update_data['part_info'] = data['part_info']
            if 'from_ques' in data:
                update_data['from_ques'] = data['from_ques']
            if 'to_ques' in data:
                update_data['to_ques'] = data['to_ques']
            if 'is_published' in data:
                update_data['is_published'] = data['is_published']

            # Handle QuestionSet update
            if 'questions_set' in data:
                questions_set_data = data['questions_set']
                questions_set = None

                if blog_data.get('questions_set'):
                    # Update existing QuestionSet
                    questions_set = QuestionSet.objects.get(id=blog_data['questions_set']['id'])
                    if 'page' in questions_set_data:
                        questions_set.page = questions_set_data['page']
                    if 'audio' in questions_set_data:
                        questions_set.audio = questions_set_data['audio']
                    if 'image' in questions_set_data:
                        questions_set.image = questions_set_data['image']
                    
                    # Update from_ques and to_ques
                    if 'from_ques' in data:
                        questions_set.from_ques = data['from_ques']
                    if 'to_ques' in data:
                        questions_set.to_ques = data['to_ques']
                    
                    questions_set.save()

                    # Update questions
                    if 'questions' in questions_set_data:
                        questions_set.question_question_set.all().delete()
                        
                        for question_data in questions_set_data['questions']:
                            # Normalize answers before saving
                            answers = normalize_answers(question_data.get('answers', {}))
                            
                            Question.objects.create(
                                question_set=questions_set,
                                question_number=question_data.get('question_number'),
                                question_text=question_data.get('question_text'),
                                correct_answer=question_data.get('correct_answer', '').upper(),  # Also uppercase correct_answer
                                difficulty_level=question_data.get('difficulty_level', ''),
                                answers=answers
                            )
                else:
                    # Create new QuestionSet with from_ques and to_ques
                    questions_set = QuestionSet.objects.create(
                        page=questions_set_data.get('page'),
                        audio=questions_set_data.get('audio'),
                        image=questions_set_data.get('image'),
                        from_ques=data.get('from_ques'),
                        to_ques=data.get('to_ques')
                    )
                    
                    # Create questions
                    if 'questions' in questions_set_data:
                        for question_data in questions_set_data['questions']:
                            # Normalize answers before saving
                            answers = normalize_answers(question_data.get('answers', {}))
                            
                            Question.objects.create(
                                question_set=questions_set,
                                question_number=question_data.get('question_number'),
                                question_text=question_data.get('question_text'),
                                correct_answer=question_data.get('correct_answer', '').upper(),  # Also uppercase correct_answer
                                difficulty_level=question_data.get('difficulty_level', ''),
                                answers=answers
                            )

                update_data['questions_set'] = questions_set

            # Update blog using repository
            affected_rows, updated_blog = self.blog_repository.update(id, update_data)
            
            if affected_rows == 0:
                raise ValidationError('Failed to update blog')
            
            return updated_blog

        except Exception as e:
            raise ValidationError(f'Failed to update blog: {str(e)}')

    def delete_blog(self, id: int, author: Any) -> bool:
        """
        Delete a blog
        
        Args:
            id: ID of blog to delete
            author: User object who is deleting the blog
        """
        try:
            # Get existing blog
            blog_data = self.blog_repository.get_one(BlogQuery(id=id))
            if not blog_data:
                raise ValidationError('Blog not found')

            # Check ownership unless user is teacher
            if not author.is_teacher and blog_data['author']['id'] != author.id:
                raise ValidationError("You don't have permission to delete this blog")

            # Delete blog using repository
            affected_rows = self.blog_repository.delete(id)
            
            if affected_rows == 0:
                raise ValidationError('Failed to delete blog')
            
            return blog_data

        except Exception as e:
            raise ValidationError(f'Failed to delete blog: {str(e)}')

    def create(self, data: Dict[str, Any], author: Any) -> Dict[str, Any]:
        """Alias for create_blog to match base interface"""
        return self.create_blog(data, author)

    def update(self, id: int, data: Dict[str, Any], author: Any) -> Dict[str, Any]:
        """Alias for update_blog to match base interface"""
        return self.update_blog(id, data, author)

    def delete(self, id: int, author: Any) -> bool:
        """Alias for delete_blog to match base interface"""
        return self.delete_blog(id, author)