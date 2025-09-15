from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from EStudyApp.serializers import QuestionSerializer
from course.toeicAI import analyze_toeic_question
from course.models.blog import Blog
from EStudyApp.models import Question, QuestionSet
from course.serializer.blog import BlogSerializer
from django.db.models import Prefetch

from course.services.blog import BlogService
from course.views.api.base import BaseCreateAPIView, BaseUpdateAPIView, BaseDeleteAPIView
from Authentication.permissions import IsTeacher
from question_bank.models import QuestionBank, QuestionSetBank

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

CACHE_TTL = 60 * 5

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_blog(request):
    user = request.user
    data = request.data
    questions_set = None

    if data['questions_set']:
        questions_set_obj = QuestionSet.objects.create(
            page=data['questions_set'],
            audio=data['audio'],
            image=data['image'],
            from_ques=data['from'],
            to_ques=data['to']
        )
        questions_set_obj.save()

        # create questions
        if data['questions']:
            questions = data['questions']
            for question in questions:
                correct_answer = question['correct_answer'] if question['correct_answer'] else ''
                question_number = question['question_number'] if question['question_number'] else None
                question_obj = Question.objects.create(
                    question_set=questions_set_obj,
                    correct_answer=correct_answer,
                    question_text=question['question'],
                    question_number=question_number,
                    answers=question['answers'],
                    deleted_at=None
                )
                question_obj.save()
        
        questions_set = questions_set_obj
        
    blog_obj = Blog.objects.create(
        author=user,
        questions_set=questions_set,
        title=data['title'],
        content=data['content'],
        part_info=data['part'],
        from_ques=data['from'],
        to_ques=data['to']
    )
    blog_obj.save()

    serializer = BlogSerializer(blog_obj).data

    return Response(serializer, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
@cache_page(CACHE_TTL, key_prefix="blog_list")
def blog_list(request):
    blogs = Blog.objects.filter(status='ACTIVE').order_by('-created_at')
    serializer = BlogSerializer(blogs, many=True).data
    return Response(serializer, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(CACHE_TTL, key_prefix="blog_detail")
def blog_detail(request, id):
    blog = Blog.objects.prefetch_related(
        Prefetch(
            'questions_set',
            queryset=QuestionSet.objects.prefetch_related(
                Prefetch('question_question_set', queryset=Question.objects.order_by('question_number'))
            )
        )
    ).get(id=id)

    # Tạo danh sách câu hỏi đã phân loại
    question_data = []

    # Kiểm tra xem blog có chứa questions_set hay không và xử lý mối quan hệ một-một
    if blog.questions_set:  # Kiểm tra nếu questions_set không phải là None
        question_set = blog.questions_set  # Lấy đối tượng QuestionSet duy nhất
        for question in question_set.question_question_set.all():  # Truy cập danh sách các câu hỏi
            # Phân loại câu hỏi vào phần TOEIC
            analyst = analyze_toeic_question(question.question_text, question.answers, question_set.audio, question_set.image)  # Phân loại câu hỏi
            print(analyst)
            # Sử dụng serializer để chuyển đổi đối tượng Question thành JSON
            question_serialized = QuestionSerializer(question).data
            # Thêm thông tin câu hỏi và phần vào danh sách
            question_data.append({
                'question': question_serialized,  # Thêm thông tin câu hỏi đã được serialize
                'analyst': analyst  # Phần của câu hỏi trong TOEIC
            })
            # Nếu cần, bạn có thể lưu thông tin part vào CSDL
            # question.save()  # Nếu bạn muốn lưu vào CSDL
        # Thêm thông tin câu hỏi và phần vào serializer
    blog_data = BlogSerializer(blog).data
    blog_data['questions_with_parts'] = question_data  # Thêm thông tin câu hỏi với phần vào response

    return Response(blog_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_blog(request, id):
    # get blog
    blog = Blog.objects.get(id=id)
    
    if blog is None:
        return Response({'message': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    
    blog.title = request.data['title']
    blog.content = request.data['content']
    blog.part_info = request.data['part']
    blog.from_ques = request.data['from']
    blog.to_ques = request.data['to']
    blog.save()
    
    # get questions set
    questions_set = QuestionSet.objects.get(id=blog.questions_set_id)
    if questions_set is None:
        return Response({'message': 'Question set not found'}, status=status.HTTP_404_NOT_FOUND)
    
    questions_set.page = request.data['questions_set']
    questions_set.save()

    # edit questions
    questions_data = request.data['questions']
    for question in questions_data:
        question_obj = Question.objects.get(id=question['id'])
        
        if question_obj is None:
            return Response({'message': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        
        question_obj.question_set = questions_set
        question_obj.question_number = question['question_number']
        question_obj.question_text = question['question']
        question_obj.correct_answer = question['correct_answer'] if question['correct_answer'] else ''
        question_obj.answers = question['answers'] if question['answers'] else ''
        question_obj.save()
    
    questions_detele_obj = Question.objects.filter(question_set=questions_set).exclude(id__in=[question['id'] for question in questions_data]).delete()
    
    new_blog = Blog.objects.get(id=id)
    serializer = BlogSerializer(new_blog).data
    return Response(serializer, status=status.HTTP_200_OK)


# panel blog list
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(CACHE_TTL, key_prefix="blog_panel")
def panel_blog_list(request):
    """
    Get list of blogs with filters and pagination
    
    Query Parameters:
        - is_published: Filter by publish status (true/false)
        - isPublished: Alias for is_published
        - page: Page number
        - per_page: Items per page
        - order_by: Sort blogs by field
            - 'is_published': Sort by publish status ascending
            - '-is_published': Sort by publish status descending
    """
    blog_service = BlogService()
    blogs = blog_service.get_blog_list(filters=request.query_params)
    return Response(blogs, status=status.HTTP_200_OK)

# panel blog detail
@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(CACHE_TTL, key_prefix="blog_panel_detail")
def panel_blog_detail(request, id):
    blog_service = BlogService()
    blog = blog_service.get_blog_detail(id)
    return Response(blog, status=status.HTTP_200_OK)

class BlogCreateView(BaseCreateAPIView):
    permission_classes = [IsAuthenticated]
    service_class = BlogService

class BlogUpdateView(BaseUpdateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    service_class = BlogService

class BlogDeleteView(BaseDeleteAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    service_class = BlogService
    
@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def panel_blog_question_bank(request, blog_id):
    """
    Add a question bank to a blog
    """
    note = request.data['note']
    
    blog = Blog.objects.get(id=blog_id)
    
    if blog is None:
        return Response({'message': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    
    question_set = blog.questions_set
    if question_set and question_set.part:
        part_description = question_set.part.part_description
    else:
        # Handle the case where part is None
        part_description = None  # Or set a default value
        # Or return an error response
        # return Response({"error": "Part not found for this question set"}, status=status.HTTP_404_NOT_FOUND)
    
    question_bank = QuestionSetBank.objects.create(
        part_description=part_description if part_description else None,
        audio=question_set.audio if question_set.audio else None,
        page=question_set.page if question_set.page else None,
        image=question_set.image if question_set.image else None,
        from_ques=question_set.from_ques if question_set.from_ques else None,
        to_ques=question_set.to_ques if question_set.to_ques else None,
        note=note if note else None
    )
    
    questions = Question.objects.filter(question_set=question_set)
    for question in questions:
        QuestionBank.objects.create(
            question_set=question_bank,
            question_type=question.question_type,
            question_text=question.question_text,
            correct_answer=question.correct_answer,
            answers=question.answers,
            part_description=part_description if part_description else None,
            difficulty_level=question.difficulty_level,
            question_number=question.question_number
        )
    
    if question_set is None:
        return Response({'message': 'Question set not found'}, status=status.HTTP_404_NOT_FOUND)
    


    return Response(status=status.HTTP_200_OK)